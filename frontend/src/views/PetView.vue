<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import Badge from "../components/Badge.vue"
import Breadcrumb from "../components/Breadcrumb.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import Modal from "../components/Modal.vue"
import PageHeader from "../components/PageHeader.vue"
import PetForm from "../components/PetForm.vue"
import SkeletonBlock from "../components/SkeletonBlock.vue"
import Timeline from "../components/Timeline.vue"
import VaccinationForm from "../components/VaccinationForm.vue"
import { ageLabel, formatDate, isBeforeDay } from "../lib/dates"
import { blankToNull } from "../lib/form"
import { presentMutation, presentQuery } from "../lib/present"
import { formatMoney } from "../lib/money"
import { visitPayStatus } from "../lib/status"
import { askConfirm } from "../lib/confirm"
import { toast } from "../lib/toast"
import { useOwner, useOwners } from "../queries/useOwners"
import { useDeletePet, usePet, usePetHistory, usePetVaccinations, usePetVisits, useUpdatePet } from "../queries/usePets"
import { useCreateVaccination, useDeleteVaccination } from "../queries/useVaccinations"

const route = useRoute()
const router = useRouter()
const petId = computed(() => String(route.params.id ?? ""))
const pet = presentQuery(usePet(petId))
const history = presentQuery(usePetHistory(petId))
const visits = presentQuery(usePetVisits(petId))
const vaccines = presentQuery(usePetVaccinations(petId))
const ownerId = computed(() => pet.data?.owner_id ?? "")
const owner = presentQuery(useOwner(ownerId))
const ownerSearch = ref("")
const owners = presentQuery(useOwners(ownerSearch))
const updatePet = presentMutation(useUpdatePet())
const deletePet = presentMutation(useDeletePet())
const createVaccine = presentMutation(useCreateVaccination())
const deleteVaccine = presentMutation(useDeleteVaccination())

const tab = ref<"overview" | "history" | "vaccinations" | "billing">("overview")
const editOpen = ref(false)
const vaccineOpen = ref(false)
const formErrors = ref<Record<string, string>>({})
const vaccineErrors = ref<Record<string, string>>({})

const age = computed(() => ageLabel(pet.data?.date_of_birth))
const tabs = [
  { id: "overview", label: "Overview" },
  { id: "history", label: "History" },
  { id: "vaccinations", label: "Vaccinations" },
  { id: "billing", label: "Billing" },
] as const

watch(
  () => pet.data?.name,
  (name) => {
    if (name) document.title = `${name} · Paw Lodge`
  },
  { immediate: true },
)

async function onEdit(value: {
  owner_id: string
  name: string
  species: string
  breed: string
  sex: string
  date_of_birth: string
  color: string
  notes: string
}) {
  formErrors.value = {}
  try {
    await updatePet.mutateAsync({
      petId: petId.value,
      body: {
        owner_id: value.owner_id,
        name: value.name,
        species: value.species,
        breed: blankToNull(value.breed),
        sex: blankToNull(value.sex),
        date_of_birth: value.date_of_birth || null,
        color: blankToNull(value.color),
        notes: blankToNull(value.notes),
      },
    })
    toast.success("Pet updated.")
    editOpen.value = false
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

async function onDelete() {
  const ok = await askConfirm({
    title: "Delete this pet?",
    message: "This cannot be undone. Pets with visits or vaccinations cannot be deleted.",
    confirmLabel: "Delete pet",
  })
  if (!ok || !pet.data) return
  try {
    await deletePet.mutateAsync(pet.data.id)
    toast.success("Pet deleted.")
    await router.push("/app/pets")
  } catch (error) {
    toast.error(errorMessage(error))
  }
}

async function onVaccine(value: {
  pet_id: string
  vaccine_name: string
  administered_date: string
  next_due_date: string
  batch_number: string
  notes: string
}) {
  vaccineErrors.value = {}
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
    vaccineOpen.value = false
    tab.value = "vaccinations"
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) vaccineErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

async function removeVaccine(id: string) {
  const ok = await askConfirm({
    title: "Remove this vaccination?",
    message: "The record will be deleted from this pet’s history.",
    confirmLabel: "Remove",
  })
  if (!ok) return
  try {
    await deleteVaccine.mutateAsync({ vaccinationId: id, petId: petId.value })
    toast.success("Vaccination removed.")
  } catch (error) {
    toast.error(errorMessage(error))
  }
}

function dueLabel(date: string | null): string {
  if (!date) return "No next due date"
  return isBeforeDay(date) ? `Overdue · due ${formatDate(date)}` : `Due ${formatDate(date)}`
}
</script>

<template>
  <ErrorNotice v-if="pet.isError" :error="pet.error" @retry="pet.refetch()" />
  <div v-else-if="pet.isPending" class="grid gap-3">
    <SkeletonBlock class-name="h-12 w-48" />
    <SkeletonBlock class-name="h-40" />
  </div>
  <template v-else-if="pet.data">
    <Breadcrumb :items="[{ label: 'Pets', to: '/app/pets' }, { label: pet.data.name }]" />
    <PageHeader :title="pet.data.name" :eyebrow="pet.data.species">
      <template #actions>
        <RouterLink
          :to="`/app/visits/new?pet=${pet.data.id}`"
          class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white"
        >
          Record visit
        </RouterLink>
        <AppButton variant="secondary" @click="vaccineOpen = true">Add vaccination</AppButton>
        <AppButton variant="secondary" @click="editOpen = true">Edit pet</AppButton>
      </template>
    </PageHeader>

    <p class="mb-4 text-sm text-muted">
      <span v-if="pet.data.breed">{{ pet.data.breed }}</span>
      <span v-if="pet.data.sex"> · {{ pet.data.sex }}</span>
      <span v-if="age"> · {{ age }}</span>
      <span v-if="owner.data">
        ·
        <RouterLink :to="`/app/owners/${owner.data.id}`" class="text-leaf underline-offset-2 hover:underline">
          {{ owner.data.name }}
        </RouterLink>
      </span>
    </p>

    <div class="mb-4 flex gap-2 overflow-x-auto" role="tablist" aria-label="Pet record">
      <button
        v-for="item in tabs"
        :id="`tab-${item.id}`"
        :key="item.id"
        type="button"
        role="tab"
        class="min-h-11 shrink-0 rounded-xl px-4 text-sm"
        :class="tab === item.id ? 'bg-spruce text-white' : 'bg-card text-ink'"
        :aria-selected="tab === item.id"
        :aria-controls="`panel-${item.id}`"
        @click="tab = item.id"
      >
        {{ item.label }}
      </button>
    </div>

    <section
      v-show="tab === 'overview'"
      id="panel-overview"
      role="tabpanel"
      aria-labelledby="tab-overview"
      class="rounded-2xl border border-line bg-card p-4"
    >
      <dl class="grid gap-4 sm:grid-cols-2">
        <div>
          <dt class="text-sm text-muted">Species</dt>
          <dd>{{ pet.data.species }}</dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Breed</dt>
          <dd>{{ pet.data.breed || "—" }}</dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Sex</dt>
          <dd>{{ pet.data.sex || "—" }}</dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Age</dt>
          <dd>{{ age || "Date of birth not recorded" }}</dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Date of birth</dt>
          <dd>{{ formatDate(pet.data.date_of_birth) }}</dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Color</dt>
          <dd>{{ pet.data.color || "—" }}</dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="text-sm text-muted">Notes</dt>
          <dd class="whitespace-pre-wrap">{{ pet.data.notes || "—" }}</dd>
        </div>
      </dl>
      <AppButton class="mt-6" variant="danger" @click="onDelete">Delete pet</AppButton>
    </section>

    <section v-show="tab === 'history'" id="panel-history" role="tabpanel" aria-labelledby="tab-history">
      <div v-if="history.isPending" class="grid gap-3">
        <SkeletonBlock class-name="h-20" />
        <SkeletonBlock class-name="h-20" />
      </div>
      <ErrorNotice v-else-if="history.isError" :error="history.error" @retry="history.refetch()" />
      <Timeline v-else :events="history.data?.timeline ?? []" />
    </section>

    <section v-show="tab === 'vaccinations'" id="panel-vaccinations" role="tabpanel" aria-labelledby="tab-vaccinations">
      <div v-if="vaccines.isPending" class="grid gap-3">
        <SkeletonBlock class-name="h-20" />
      </div>
      <ErrorNotice v-else-if="vaccines.isError" :error="vaccines.error" @retry="vaccines.refetch()" />
      <EmptyState
        v-else-if="!vaccines.data?.length"
        title="No vaccinations"
        body="Record the first vaccine for this pet."
      >
        <AppButton @click="vaccineOpen = true">Add vaccination</AppButton>
      </EmptyState>
      <ul v-else class="grid gap-3">
        <li v-for="item in vaccines.data" :key="item.id" class="rounded-2xl border border-line bg-card p-4">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-medium">{{ item.vaccine_name }}</p>
              <p class="mt-1 text-sm text-muted">Given {{ formatDate(item.administered_date) }}</p>
              <Badge class="mt-2" :tone="item.next_due_date && isBeforeDay(item.next_due_date) ? 'danger' : 'warn'">
                {{ dueLabel(item.next_due_date) }}
              </Badge>
              <p v-if="item.batch_number" class="mt-2 text-sm text-muted">Batch {{ item.batch_number }}</p>
              <p v-if="item.notes" class="mt-2 text-sm">{{ item.notes }}</p>
            </div>
            <AppButton variant="ghost" @click="removeVaccine(item.id)">Remove</AppButton>
          </div>
        </li>
      </ul>
    </section>

    <section v-show="tab === 'billing'" id="panel-billing" role="tabpanel" aria-labelledby="tab-billing">
      <div v-if="visits.isPending" class="grid gap-3">
        <SkeletonBlock class-name="h-20" />
      </div>
      <ErrorNotice v-else-if="visits.isError" :error="visits.error" @retry="visits.refetch()" />
      <EmptyState v-else-if="!visits.data?.length" title="No visits yet" body="A visit records treatments and the amount due.">
        <RouterLink
          :to="`/app/visits/new?pet=${pet.data.id}`"
          class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white"
        >
          Record visit
        </RouterLink>
      </EmptyState>
      <ul v-else class="grid gap-3">
        <li v-for="visit in visits.data" :key="visit.id">
          <RouterLink :to="`/app/visits/${visit.id}`" class="block rounded-2xl border border-line bg-card p-4">
            <span class="flex flex-wrap items-center justify-between gap-2">
              <span class="font-medium">{{ visit.diagnosis || "Visit" }}</span>
              <Badge :tone="visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).tone">
                {{ visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).label }}
              </Badge>
            </span>
            <span class="mt-1 block text-sm text-muted">{{ formatDate(visit.visit_date) }}</span>
            <span class="mt-2 block text-sm">
              Total {{ formatMoney(visit.total) }} · Outstanding {{ formatMoney(visit.outstanding) }}
            </span>
          </RouterLink>
        </li>
      </ul>
    </section>

    <Modal :open="editOpen" title="Edit pet" @close="editOpen = false">
      <PetForm
        :owners="owners.data ?? []"
        :initial="pet.data"
        :submitting="updatePet.isPending"
        :errors="formErrors"
        @submit="onEdit"
      />
    </Modal>
    <Modal :open="vaccineOpen" title="Add vaccination" @close="vaccineOpen = false">
      <VaccinationForm
        :pets="pet.data ? [pet.data] : []"
        :locked-pet-id="pet.data.id"
        :submitting="createVaccine.isPending"
        :errors="vaccineErrors"
        @submit="onVaccine"
      />
    </Modal>
  </template>
</template>
