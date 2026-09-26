<script setup lang="ts">
import { computed, ref } from "vue"
import { useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import type { Pet } from "../api/types"
import AppButton from "../components/AppButton.vue"
import DataTable from "../components/DataTable.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import MobileList from "../components/MobileList.vue"
import Modal from "../components/Modal.vue"
import PageHeader from "../components/PageHeader.vue"
import PetForm from "../components/PetForm.vue"
import SearchInput from "../components/SearchInput.vue"
import SkeletonBlock from "../components/SkeletonBlock.vue"
import { blankToNull } from "../lib/form"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { useDebounced } from "../lib/debounce"
import { useCreateOwner, useOwners } from "../queries/useOwners"
import { useCreatePet, usePets } from "../queries/usePets"

const router = useRouter()
const searchInput = ref("")
const speciesInput = ref("")
const search = useDebounced(searchInput)
const species = useDebounced(speciesInput)
const pets = presentQuery(usePets(search, species))
const ownerSearch = ref("")
const owners = presentQuery(useOwners(ownerSearch))
const createPet = presentMutation(useCreatePet())
const createOwner = presentMutation(useCreateOwner())

const formOpen = ref(false)
const formErrors = ref<Record<string, string>>({})
const pinnedOwnerId = ref("")

const ownerName = (id: string) => owners.data?.find((owner) => owner.id === id)?.name ?? "Owner"
const filtering = computed(() => Boolean(search.value.trim() || species.value.trim()))

function openForm() {
  formErrors.value = {}
  pinnedOwnerId.value = ""
  formOpen.value = true
}

async function onCreate(value: {
  owner_id: string
  newOwner: { name: string; phone: string; email: string } | null
  name: string
  species: string
  breed: string
  sex: string
  date_of_birth: string
  color: string
  notes: string
}) {
  formErrors.value = {}
  let ownerId = pinnedOwnerId.value || value.owner_id
  try {
    if (value.newOwner && !pinnedOwnerId.value) {
      const owner = await createOwner.mutateAsync({
        name: value.newOwner.name,
        phone: value.newOwner.phone,
        email: blankToNull(value.newOwner.email),
      })
      pinnedOwnerId.value = owner.id
      ownerId = owner.id
    }
    const pet = await createPet.mutateAsync({
      owner_id: ownerId,
      name: value.name,
      species: value.species,
      breed: blankToNull(value.breed),
      sex: blankToNull(value.sex),
      date_of_birth: value.date_of_birth || null,
      color: blankToNull(value.color),
      notes: blankToNull(value.notes),
    })
    toast.success(`${pet.name} added.`)
    formOpen.value = false
    await router.push(`/app/pets/${pet.id}`)
  } catch (error) {
    if (pinnedOwnerId.value && value.newOwner) {
      toast.warning("The owner was saved. The pet was not.")
    }
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

function petMeta(pet: Pet): string {
  return [pet.species, pet.breed].filter(Boolean).join(" · ")
}
</script>

<template>
  <PageHeader title="Pets" description="Search by name, then open the record you need.">
    <template #actions>
      <AppButton @click="openForm">Add pet</AppButton>
    </template>
  </PageHeader>

  <div class="mb-4 grid gap-3 sm:grid-cols-2">
    <SearchInput id="pet-search" v-model="searchInput" label="Search pets" />
    <SearchInput id="pet-species" v-model="speciesInput" label="Species" />
  </div>
  <p class="mb-4 text-sm text-muted">Species matches the full name, for example Dog. Search matches part of the pet’s name.</p>

  <ErrorNotice v-if="pets.isError" :error="pets.error" @retry="pets.refetch()" />
  <div v-else-if="pets.isPending" class="grid gap-3">
    <SkeletonBlock class-name="h-20" />
    <SkeletonBlock class-name="h-20" />
    <SkeletonBlock class-name="h-20" />
  </div>
  <EmptyState
    v-else-if="!pets.data?.length && !filtering"
    title="No pets yet"
    body="Add the first pet. You can create their owner in the same step."
  >
    <AppButton @click="openForm">Add pet</AppButton>
  </EmptyState>
  <EmptyState
    v-else-if="!pets.data?.length"
    title="No pets match"
    body="Try a different name, or clear the species filter."
  >
    <AppButton
      variant="secondary"
      @click="
        searchInput = '';
        speciesInput = ''
      "
    >
      Clear search
    </AppButton>
  </EmptyState>
  <template v-else>
    <DataTable>
      <thead class="bg-paper text-muted">
        <tr>
          <th class="px-4 py-3 font-medium" scope="col">Name</th>
          <th class="px-4 py-3 font-medium" scope="col">Species</th>
          <th class="px-4 py-3 font-medium" scope="col">Breed</th>
          <th class="px-4 py-3 font-medium" scope="col">Owner</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pet in pets.data" :key="pet.id" class="border-t border-line">
          <td class="px-4 py-3">
            <RouterLink :to="`/app/pets/${pet.id}`" class="font-medium text-leaf underline-offset-2 hover:underline">
              {{ pet.name }}
            </RouterLink>
          </td>
          <td class="px-4 py-3">{{ pet.species }}</td>
          <td class="px-4 py-3">{{ pet.breed || "—" }}</td>
          <td class="px-4 py-3">{{ ownerName(pet.owner_id) }}</td>
        </tr>
      </tbody>
    </DataTable>
    <MobileList>
      <RouterLink
        v-for="pet in pets.data"
        :key="pet.id"
        :to="`/app/pets/${pet.id}`"
        class="block rounded-2xl border border-line bg-card p-4"
      >
        <span class="block font-medium">{{ pet.name }}</span>
        <span class="mt-1 block text-sm text-muted">{{ petMeta(pet) }}</span>
        <span class="mt-1 block text-sm">{{ ownerName(pet.owner_id) }}</span>
      </RouterLink>
    </MobileList>
  </template>

  <Modal :open="formOpen" title="Add pet" @close="formOpen = false">
    <PetForm
      :owners="owners.data ?? []"
      :submitting="createPet.isPending || createOwner.isPending"
      :errors="formErrors"
      :pinned-owner-id="pinnedOwnerId"
      allow-new-owner
      @submit="onCreate"
    />
  </Modal>
</template>
