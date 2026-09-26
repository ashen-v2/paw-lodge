<script setup lang="ts">
import { ref } from "vue"

import type { Service } from "../api/types"
import { moneyInput } from "../lib/form"
import AppButton from "./AppButton.vue"
import AppField from "./AppField.vue"
import AppInput from "./AppInput.vue"
import AppTextarea from "./AppTextarea.vue"

const props = defineProps<{
  initial?: Service | null
  submitting: boolean
  errors: Record<string, string>
}>()

const emit = defineEmits<{
  submit: [value: { name: string; description: string; price: string; is_active: boolean }]
}>()

const name = ref(props.initial?.name ?? "")
const description = ref(props.initial?.description ?? "")
const price = ref(props.initial ? moneyInput(props.initial.price) : "")
const active = ref(props.initial?.is_active ?? true)
const local = ref<Record<string, string>>({})

function message(key: string): string {
  return local.value[key] || props.errors[key] || ""
}

function onSubmit() {
  local.value = {}
  if (!name.value.trim()) local.value.name = "Enter a service name."
  const raw = String(price.value ?? "").trim()
  const amount = Number(raw)
  if (raw === "" || !Number.isFinite(amount) || amount < 0) {
    local.value.price = "Enter a price of zero or more."
  }
  if (Object.keys(local.value).length) return
  emit("submit", {
    name: name.value.trim(),
    description: description.value.trim(),
    price: amount.toFixed(2),
    is_active: active.value,
  })
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="onSubmit">
    <AppField label="Name" field-id="service-name" :error="message('name')">
      <AppInput id="service-name" v-model="name" maxlength="255" :invalid="Boolean(message('name'))" />
    </AppField>
    <AppField label="Description" field-id="service-description" hint="Optional.">
      <AppTextarea id="service-description" v-model="description" :rows="3" />
    </AppField>
    <AppField label="Price" field-id="service-price" :error="message('price')">
      <AppInput
        id="service-price"
        v-model="price"
        type="number"
        min="0"
        step="0.01"
        inputmode="decimal"
        :invalid="Boolean(message('price'))"
      />
    </AppField>
    <label class="flex min-h-11 items-center gap-3 text-sm">
      <input v-model="active" type="checkbox" class="size-5 accent-leaf" />
      Active — offered when recording a visit
    </label>
    <AppButton type="submit" :disabled="submitting">{{ submitting ? "Saving…" : initial ? "Save service" : "Add service" }}</AppButton>
  </form>
</template>
