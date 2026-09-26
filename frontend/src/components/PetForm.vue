<script setup lang="ts">
import { ref, watch } from "vue"

import type { Owner, Pet } from "../api/types"
import AppButton from "./AppButton.vue"
import AppField from "./AppField.vue"
import AppInput from "./AppInput.vue"
import AppSelect from "./AppSelect.vue"
import AppTextarea from "./AppTextarea.vue"

const props = defineProps<{
  owners: Owner[]
  initial?: Pet | null
  submitting: boolean
  errors: Record<string, string>
  allowNewOwner?: boolean
  pinnedOwnerId?: string
}>()

const emit = defineEmits<{
  submit: [
    value: {
      owner_id: string
      newOwner: { name: string; phone: string; email: string } | null
      name: string
      species: string
      breed: string
      sex: string
      date_of_birth: string
      color: string
      notes: string
    },
  ]
}>()

const ownerId = ref(props.initial?.owner_id ?? props.owners[0]?.id ?? "")
const makingOwner = ref(Boolean(props.allowNewOwner) && props.owners.length === 0 && !props.initial)
const ownerName = ref("")
const ownerPhone = ref("")
const ownerEmail = ref("")
const name = ref(props.initial?.name ?? "")
const species = ref(props.initial?.species ?? "")
const breed = ref(props.initial?.breed ?? "")
const sex = ref(props.initial?.sex ?? "")
const dateOfBirth = ref(props.initial?.date_of_birth ?? "")
const color = ref(props.initial?.color ?? "")
const notes = ref(props.initial?.notes ?? "")
const local = ref<Record<string, string>>({})

watch(
  () => props.owners,
  (owners) => {
    if (!ownerId.value && owners[0] && !makingOwner.value) ownerId.value = owners[0].id
  },
)

watch(
  () => props.pinnedOwnerId,
  (id) => {
    if (!id) return
    makingOwner.value = false
    ownerId.value = id
  },
)

function message(key: string): string {
  return local.value[key] || props.errors[key] || ""
}

function onSubmit() {
  local.value = {}
  if (makingOwner.value) {
    if (!ownerName.value.trim()) local.value.owner_name = "Enter the owner's name."
    if (!ownerPhone.value.trim()) local.value.owner_phone = "Enter a phone number."
  } else if (!ownerId.value) {
    local.value.owner_id = "Choose an owner."
  }
  if (!name.value.trim()) local.value.name = "Enter the pet's name."
  if (!species.value.trim()) local.value.species = "Enter a species."
  if (Object.keys(local.value).length) return
  emit("submit", {
    owner_id: makingOwner.value ? "" : ownerId.value,
    newOwner: makingOwner.value
      ? { name: ownerName.value.trim(), phone: ownerPhone.value.trim(), email: ownerEmail.value.trim() }
      : null,
    name: name.value.trim(),
    species: species.value.trim(),
    breed: breed.value.trim(),
    sex: sex.value.trim(),
    date_of_birth: dateOfBirth.value,
    color: color.value.trim(),
    notes: notes.value.trim(),
  })
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="onSubmit">
    <div v-if="allowNewOwner && !initial" class="flex flex-wrap gap-2">
      <AppButton type="button" :variant="makingOwner ? 'secondary' : 'primary'" @click="makingOwner = false" :disabled="owners.length === 0">
        Existing owner
      </AppButton>
      <AppButton type="button" :variant="makingOwner ? 'primary' : 'secondary'" @click="makingOwner = true">
        New owner
      </AppButton>
    </div>

    <AppField v-if="makingOwner" label="Owner name" field-id="pet-owner-name" :error="message('owner_name')">
      <AppInput id="pet-owner-name" v-model="ownerName" maxlength="255" :invalid="Boolean(message('owner_name'))" />
    </AppField>
    <AppField v-if="makingOwner" label="Owner phone" field-id="pet-owner-phone" :error="message('owner_phone')">
      <AppInput id="pet-owner-phone" v-model="ownerPhone" type="tel" maxlength="50" :invalid="Boolean(message('owner_phone'))" />
    </AppField>
    <AppField v-if="makingOwner" label="Owner email" field-id="pet-owner-email" :error="message('email')" hint="Optional.">
      <AppInput id="pet-owner-email" v-model="ownerEmail" type="email" :invalid="Boolean(message('email'))" />
    </AppField>
    <AppField v-else label="Owner" field-id="pet-owner" :error="message('owner_id')">
      <AppSelect id="pet-owner" v-model="ownerId" :invalid="Boolean(message('owner_id'))">
        <option v-if="owners.length === 0" value="">No owners yet</option>
        <option v-for="owner in owners" :key="owner.id" :value="owner.id">{{ owner.name }}</option>
      </AppSelect>
    </AppField>

    <AppField label="Pet name" field-id="pet-name" :error="message('name')">
      <AppInput id="pet-name" v-model="name" maxlength="255" :invalid="Boolean(message('name'))" />
    </AppField>
    <AppField label="Species" field-id="pet-species" :error="message('species')" hint="Any species. Dog and Cat are suggestions.">
      <AppInput id="pet-species" v-model="species" maxlength="100" list="species-suggestions" :invalid="Boolean(message('species'))" />
      <datalist id="species-suggestions">
        <option value="Dog" />
        <option value="Cat" />
        <option value="Rabbit" />
        <option value="Bird" />
      </datalist>
    </AppField>
    <AppField label="Breed" field-id="pet-breed" hint="Optional.">
      <AppInput id="pet-breed" v-model="breed" maxlength="100" />
    </AppField>
    <AppField label="Sex" field-id="pet-sex" hint="Optional.">
      <AppInput id="pet-sex" v-model="sex" maxlength="20" list="sex-suggestions" />
      <datalist id="sex-suggestions">
        <option value="Female" />
        <option value="Male" />
        <option value="Unknown" />
      </datalist>
    </AppField>
    <AppField label="Date of birth" field-id="pet-dob" hint="Optional. Used to show age.">
      <AppInput id="pet-dob" v-model="dateOfBirth" type="date" />
    </AppField>
    <AppField label="Color" field-id="pet-color" hint="Optional.">
      <AppInput id="pet-color" v-model="color" maxlength="50" />
    </AppField>
    <AppField label="Notes" field-id="pet-notes" hint="Optional.">
      <AppTextarea id="pet-notes" v-model="notes" :rows="3" />
    </AppField>
    <AppButton type="submit" :disabled="submitting">{{ submitting ? "Saving…" : initial ? "Save pet" : "Add pet" }}</AppButton>
  </form>
</template>
