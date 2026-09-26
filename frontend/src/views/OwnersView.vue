<script setup lang="ts">
import { computed, ref } from "vue"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import DataTable from "../components/DataTable.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import MobileList from "../components/MobileList.vue"
import Modal from "../components/Modal.vue"
import OwnerForm from "../components/OwnerForm.vue"
import PageHeader from "../components/PageHeader.vue"
import SearchInput from "../components/SearchInput.vue"
import SkeletonBlock from "../components/SkeletonBlock.vue"
import { useDebounced } from "../lib/debounce"
import { blankToNull } from "../lib/form"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { useCreateOwner, useOwners } from "../queries/useOwners"

const searchInput = ref("")
const search = useDebounced(searchInput)
const owners = presentQuery(useOwners(search))
const createOwner = presentMutation(useCreateOwner())
const formOpen = ref(false)
const formErrors = ref<Record<string, string>>({})
const filtering = computed(() => Boolean(search.value.trim()))

async function onCreate(value: { name: string; phone: string; email: string; address: string }) {
  formErrors.value = {}
  try {
    const owner = await createOwner.mutateAsync({
      name: value.name,
      phone: value.phone,
      email: blankToNull(value.email),
      address: blankToNull(value.address),
    })
    toast.success(`${owner.name} added.`)
    formOpen.value = false
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}
</script>

<template>
  <PageHeader title="Owners" description="People who bring pets to the clinic.">
    <template #actions>
      <AppButton @click="formOpen = true">Add owner</AppButton>
    </template>
  </PageHeader>

  <div class="mb-4 max-w-md">
    <SearchInput id="owner-search" v-model="searchInput" label="Search owners" />
  </div>
  <p class="mb-4 text-sm text-muted">Matches name, phone, or email.</p>

  <ErrorNotice v-if="owners.isError" :error="owners.error" @retry="owners.refetch()" />
  <div v-else-if="owners.isPending" class="grid gap-3">
    <SkeletonBlock class-name="h-20" />
    <SkeletonBlock class-name="h-20" />
  </div>
  <EmptyState v-else-if="!owners.data?.length && !filtering" title="No owners yet" body="Add the person first, then their pets.">
    <AppButton @click="formOpen = true">Add owner</AppButton>
  </EmptyState>
  <EmptyState v-else-if="!owners.data?.length" title="No owners match" body="Try another name, phone, or email.">
    <AppButton variant="secondary" @click="searchInput = ''">Clear search</AppButton>
  </EmptyState>
  <template v-else>
    <DataTable>
      <thead class="bg-paper text-muted">
        <tr>
          <th class="px-4 py-3 font-medium" scope="col">Name</th>
          <th class="px-4 py-3 font-medium" scope="col">Phone</th>
          <th class="px-4 py-3 font-medium" scope="col">Email</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="owner in owners.data" :key="owner.id" class="border-t border-line">
          <td class="px-4 py-3">
            <RouterLink :to="`/app/owners/${owner.id}`" class="font-medium text-leaf underline-offset-2 hover:underline">
              {{ owner.name }}
            </RouterLink>
          </td>
          <td class="px-4 py-3">{{ owner.phone }}</td>
          <td class="px-4 py-3">{{ owner.email || "—" }}</td>
        </tr>
      </tbody>
    </DataTable>
    <MobileList>
      <RouterLink
        v-for="owner in owners.data"
        :key="owner.id"
        :to="`/app/owners/${owner.id}`"
        class="block rounded-2xl border border-line bg-card p-4"
      >
        <span class="block font-medium">{{ owner.name }}</span>
        <span class="mt-1 block text-sm">{{ owner.phone }}</span>
        <span v-if="owner.email" class="mt-1 block text-sm text-muted">{{ owner.email }}</span>
      </RouterLink>
    </MobileList>
  </template>

  <Modal :open="formOpen" title="Add owner" @close="formOpen = false">
    <OwnerForm :submitting="createOwner.isPending" :errors="formErrors" @submit="onCreate" />
  </Modal>
</template>
