<script setup lang="ts">
import { computed, ref } from "vue"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import Badge from "../components/Badge.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import Modal from "../components/Modal.vue"
import PageHeader from "../components/PageHeader.vue"
import VaccinationForm from "../components/VaccinationForm.vue"
import { formatDate, isBeforeDay, utcToday } from "../lib/dates"
import { blankToNull } from "../lib/form"
import { askConfirm } from "../lib/confirm"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { usePets } from "../queries/usePets"
import { useCreateVaccination, useDeleteVaccination, useUpcoming, useVaccinations } from "../queries/useVaccinations"

const days = ref(30)
const upcoming = presentQuery(useUpcoming(days))
const all = presentQuery(useVaccinations())
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const createVaccine = presentMutation(useCreateVaccination())
const removeVaccine = presentMutation(useDeleteVaccination())

const formOpen = ref(false)
const formErrors = ref<Record<string, string>>({})
const presets = [7, 30, 90]

const petName = (id: string) => pets.data?.find((pet) => pet.id === id)?.name ?? "Pet"

const overdue = computed(() =>
  (all.data ?? [])
    .filter((item) => isBeforeDay(item.next_due_date, utcToday()))
    .slice()
    .sort((a, b) => (a.next_due_date ?? "").localeCompare(b.next_due_date ?? "")),
)

async function onCreate(value: {
  pet_id: string
  vaccine_name: string
  administered_date: string
  next_due_date: string
  batch_number: string
  notes: string
}) {
  formErrors.value = {}
  try {
    await createVaccine.mutateAsync({
      pet_id: value.pet_id,
      vaccine_name: value.vaccine_name,
      administered_date: value.administered_date,
      next_due_date: value.next_due_date || null,
      batch_number: blankToNull(value.batch_number),
      notes: blankToNull(value.notes),
    })
    toast.success("Vaccination recorded.")
    formOpen.value = false
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

async function onRemove(id: string, petId: string) {
  const ok = await askConfirm({
    title: "Remove this vaccination?",
    message: "The record will be deleted from the pet’s history.",
    confirmLabel: "Remove",
  })
  if (!ok) return
  try {
    await removeVaccine.mutateAsync({ vaccinationId: id, petId })
    toast.success("Vaccination removed.")
  } catch (error) {
    toast.error(errorMessage(error))
  }
}
</script>

<template>
  <PageHeader title="Vaccinations" description="Due dates come from the clinic server. Overdue means the next due date is before today (UTC).">
    <template #actions>
      <AppButton @click="formOpen = true">Record vaccination</AppButton>
    </template>
  </PageHeader>

  <div class="mb-4 flex flex-wrap gap-2" role="group" aria-label="Upcoming window">
    <AppButton
      v-for="preset in presets"
      :key="preset"
      type="button"
      :variant="days === preset ? 'primary' : 'secondary'"
      @click="days = preset"
    >
      {{ preset }} days
    </AppButton>
  </div>

  <section>
    <h2 class="mb-3 font-serif text-2xl">Overdue</h2>
    <ErrorNotice v-if="all.isError" :error="all.error" @retry="all.refetch()" />
    <p v-else-if="!overdue.length" class="text-sm text-muted">No overdue vaccinations.</p>
    <ul v-else class="grid gap-3">
      <li v-for="item in overdue" :key="item.id" class="rounded-2xl border border-line bg-card p-4">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <RouterLink :to="`/app/pets/${item.pet_id}`" class="font-medium text-leaf underline-offset-2 hover:underline">
              {{ petName(item.pet_id) }}
            </RouterLink>
            <p class="mt-1 text-sm">{{ item.vaccine_name }}</p>
            <Badge class="mt-2" tone="danger">Overdue · due {{ formatDate(item.next_due_date) }}</Badge>
          </div>
          <AppButton variant="ghost" @click="onRemove(item.id, item.pet_id)">Remove</AppButton>
        </div>
      </li>
    </ul>
  </section>

  <section class="mt-8">
    <h2 class="mb-3 font-serif text-2xl">Upcoming</h2>
    <ErrorNotice v-if="upcoming.isError" :error="upcoming.error" @retry="upcoming.refetch()" />
    <EmptyState
      v-else-if="upcoming.data && !upcoming.data.length"
      title="Nothing due in this window"
      body="Record a vaccination with a next due date, or widen the window."
    >
      <AppButton @click="formOpen = true">Record vaccination</AppButton>
    </EmptyState>
    <ul v-else class="grid gap-3">
      <li v-for="item in upcoming.data" :key="item.id" class="rounded-2xl border border-line bg-card p-4">
        <RouterLink :to="`/app/pets/${item.pet_id}`" class="font-medium text-leaf underline-offset-2 hover:underline">
          {{ petName(item.pet_id) }}
        </RouterLink>
        <p class="mt-1 text-sm">{{ item.vaccine_name }}</p>
        <Badge class="mt-2" tone="warn">Due {{ formatDate(item.next_due_date) }}</Badge>
        <p class="mt-2 text-sm text-muted">Given {{ formatDate(item.administered_date) }}</p>
      </li>
    </ul>
  </section>

  <Modal :open="formOpen" title="Record vaccination" @close="formOpen = false">
    <VaccinationForm
      v-if="formOpen"
      :pets="pets.data ?? []"
      :submitting="createVaccine.isPending"
      :errors="formErrors"
      @submit="onCreate"
    />
  </Modal>
</template>
