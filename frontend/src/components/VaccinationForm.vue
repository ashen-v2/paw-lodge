<script setup lang="ts">
import { ref } from "vue"

import type { Pet } from "../api/types"
import { utcToday } from "../lib/dates"
import AppButton from "./AppButton.vue"
import AppField from "./AppField.vue"
import AppInput from "./AppInput.vue"
import AppSelect from "./AppSelect.vue"
import AppTextarea from "./AppTextarea.vue"

const props = defineProps<{
  pets: Pet[]
  lockedPetId?: string
  submitting: boolean
  errors: Record<string, string>
}>()

const emit = defineEmits<{
  submit: [
    value: {
      pet_id: string
      vaccine_name: string
      administered_date: string
      next_due_date: string
      batch_number: string
      notes: string
    },
  ]
}>()

const petId = ref(props.lockedPetId || props.pets[0]?.id || "")
const vaccineName = ref("")
const administered = ref(utcToday())
const nextDue = ref("")
const batch = ref("")
const notes = ref("")
const local = ref<Record<string, string>>({})

function message(key: string): string {
  return local.value[key] || props.errors[key] || ""
}

function onSubmit() {
  local.value = {}
  const chosen = props.lockedPetId || petId.value
  if (!chosen) local.value.pet_id = "Choose a pet."
  if (!vaccineName.value.trim()) local.value.vaccine_name = "Enter the vaccine name."
  if (!administered.value) local.value.administered_date = "Enter the date given."
  if (nextDue.value && administered.value && nextDue.value < administered.value) {
    local.value.next_due_date = "The next due date is before the vaccination date."
  }
  if (Object.keys(local.value).length) return
  emit("submit", {
    pet_id: chosen,
    vaccine_name: vaccineName.value.trim(),
    administered_date: administered.value,
    next_due_date: nextDue.value,
    batch_number: batch.value.trim(),
    notes: notes.value.trim(),
  })
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="onSubmit">
    <AppField v-if="!lockedPetId" label="Pet" field-id="vaccine-pet" :error="message('pet_id')">
      <AppSelect id="vaccine-pet" v-model="petId" :invalid="Boolean(message('pet_id'))">
        <option v-if="pets.length === 0" value="">No pets yet</option>
        <option v-for="pet in pets" :key="pet.id" :value="pet.id">{{ pet.name }} · {{ pet.species }}</option>
      </AppSelect>
    </AppField>
    <AppField label="Vaccine" field-id="vaccine-name" :error="message('vaccine_name')">
      <AppInput id="vaccine-name" v-model="vaccineName" maxlength="255" :invalid="Boolean(message('vaccine_name'))" />
    </AppField>
    <AppField label="Date given" field-id="vaccine-date" :error="message('administered_date')">
      <AppInput id="vaccine-date" v-model="administered" type="date" :invalid="Boolean(message('administered_date'))" />
    </AppField>
    <AppField label="Next due" field-id="vaccine-due" :error="message('next_due_date')" hint="Optional.">
      <AppInput id="vaccine-due" v-model="nextDue" type="date" :invalid="Boolean(message('next_due_date'))" />
    </AppField>
    <AppField label="Batch number" field-id="vaccine-batch" hint="Optional.">
      <AppInput id="vaccine-batch" v-model="batch" maxlength="100" />
    </AppField>
    <AppField label="Notes" field-id="vaccine-notes" hint="Optional.">
      <AppTextarea id="vaccine-notes" v-model="notes" :rows="3" />
    </AppField>
    <AppButton type="submit" :disabled="submitting">{{ submitting ? "Saving…" : "Save vaccination" }}</AppButton>
  </form>
</template>
