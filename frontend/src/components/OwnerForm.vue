<script setup lang="ts">
import { ref } from "vue"

import type { Owner } from "../api/types"
import AppButton from "./AppButton.vue"
import AppField from "./AppField.vue"
import AppInput from "./AppInput.vue"
import AppTextarea from "./AppTextarea.vue"

const props = defineProps<{
  initial?: Owner | null
  submitting: boolean
  errors: Record<string, string>
}>()

const emit = defineEmits<{
  submit: [value: { name: string; phone: string; email: string; address: string }]
}>()

const name = ref(props.initial?.name ?? "")
const phone = ref(props.initial?.phone ?? "")
const email = ref(props.initial?.email ?? "")
const address = ref(props.initial?.address ?? "")
const local = ref<Record<string, string>>({})

function message(key: string): string {
  return local.value[key] || props.errors[key] || ""
}

function onSubmit() {
  local.value = {}
  if (!name.value.trim()) local.value.name = "Enter the owner's name."
  if (!phone.value.trim()) local.value.phone = "Enter a phone number."
  if (Object.keys(local.value).length) return
  emit("submit", {
    name: name.value.trim(),
    phone: phone.value.trim(),
    email: email.value.trim(),
    address: address.value.trim(),
  })
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="onSubmit">
    <AppField label="Name" field-id="owner-name" :error="message('name')">
      <AppInput id="owner-name" v-model="name" autocomplete="name" maxlength="255" :invalid="Boolean(message('name'))" />
    </AppField>
    <AppField label="Phone" field-id="owner-phone" :error="message('phone')">
      <AppInput id="owner-phone" v-model="phone" type="tel" autocomplete="tel" maxlength="50" :invalid="Boolean(message('phone'))" />
    </AppField>
    <AppField label="Email" field-id="owner-email" :error="message('email')" hint="Optional.">
      <AppInput id="owner-email" v-model="email" type="email" autocomplete="email" :invalid="Boolean(message('email'))" />
    </AppField>
    <AppField label="Address" field-id="owner-address" :error="message('address')" hint="Optional.">
      <AppTextarea id="owner-address" v-model="address" :rows="3" :invalid="Boolean(message('address'))" />
    </AppField>
    <AppButton type="submit" :disabled="submitting">{{ submitting ? "Saving…" : initial ? "Save owner" : "Add owner" }}</AppButton>
  </form>
</template>
