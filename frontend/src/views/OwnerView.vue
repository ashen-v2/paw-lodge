<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import Breadcrumb from "../components/Breadcrumb.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import Modal from "../components/Modal.vue"
import OwnerForm from "../components/OwnerForm.vue"
import PageHeader from "../components/PageHeader.vue"
import { askConfirm } from "../lib/confirm"
import { blankToNull } from "../lib/form"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { useDeleteOwner, useOwner, useUpdateOwner } from "../queries/useOwners"
import { usePets } from "../queries/usePets"

const route = useRoute()
const router = useRouter()
const ownerId = computed(() => String(route.params.id ?? ""))
const owner = presentQuery(useOwner(ownerId))
const updateOwner = presentMutation(useUpdateOwner())
const deleteOwner = presentMutation(useDeleteOwner())
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const editOpen = ref(false)
const formErrors = ref<Record<string, string>>({})

const theirPets = computed(() => (pets.data ?? []).filter((pet) => pet.owner_id === ownerId.value))

watch(
  () => owner.data?.name,
  (name) => {
    if (name) document.title = `${name} · Paw Lodge`
  },
  { immediate: true },
)

async function onEdit(value: { name: string; phone: string; email: string; address: string }) {
  formErrors.value = {}
  try {
    await updateOwner.mutateAsync({
      ownerId: ownerId.value,
      body: {
        name: value.name,
        phone: value.phone,
        email: blankToNull(value.email),
        address: blankToNull(value.address),
      },
    })
    toast.success("Owner updated.")
    editOpen.value = false
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

async function onDelete() {
  const ok = await askConfirm({
    title: "Delete this owner?",
    message: "This cannot be undone. Owners who still have pets cannot be deleted.",
    confirmLabel: "Delete owner",
  })
  if (!ok) return
  try {
    await deleteOwner.mutateAsync(ownerId.value)
    toast.success("Owner deleted.")
    await router.push("/app/owners")
  } catch (error) {
    toast.error(errorMessage(error))
  }
}
</script>

<template>
  <ErrorNotice v-if="owner.isError" :error="owner.error" @retry="owner.refetch()" />
  <template v-else-if="owner.data">
    <Breadcrumb :items="[{ label: 'Owners', to: '/app/owners' }, { label: owner.data.name }]" />
    <PageHeader :title="owner.data.name" eyebrow="Owner">
      <template #actions>
        <AppButton variant="secondary" @click="editOpen = true">Edit owner</AppButton>
      </template>
    </PageHeader>

    <section class="rounded-2xl border border-line bg-card p-4">
      <dl class="grid gap-4 sm:grid-cols-2">
        <div>
          <dt class="text-sm text-muted">Phone</dt>
          <dd><a class="underline-offset-2 hover:underline" :href="`tel:${owner.data.phone}`">{{ owner.data.phone }}</a></dd>
        </div>
        <div>
          <dt class="text-sm text-muted">Email</dt>
          <dd>
            <a v-if="owner.data.email" class="underline-offset-2 hover:underline" :href="`mailto:${owner.data.email}`">
              {{ owner.data.email }}
            </a>
            <span v-else>—</span>
          </dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="text-sm text-muted">Address</dt>
          <dd class="whitespace-pre-wrap">{{ owner.data.address || "—" }}</dd>
        </div>
      </dl>
      <AppButton class="mt-6" variant="danger" @click="onDelete">Delete owner</AppButton>
    </section>

    <section class="mt-6">
      <h2 class="mb-3 font-serif text-2xl">Pets</h2>
      <ErrorNotice v-if="pets.isError" :error="pets.error" @retry="pets.refetch()" />
      <EmptyState v-else-if="!theirPets.length && !pets.isPending" title="No pets for this owner" body="Add a pet and choose this owner.">
        <RouterLink to="/app/pets" class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white">
          Go to pets
        </RouterLink>
      </EmptyState>
      <ul v-else class="grid gap-3">
        <li v-for="pet in theirPets" :key="pet.id">
          <RouterLink :to="`/app/pets/${pet.id}`" class="block rounded-2xl border border-line bg-card p-4">
            <span class="font-medium">{{ pet.name }}</span>
            <span class="mt-1 block text-sm text-muted">{{ pet.species }}<template v-if="pet.breed"> · {{ pet.breed }}</template></span>
          </RouterLink>
        </li>
      </ul>
    </section>

    <Modal :open="editOpen" title="Edit owner" @close="editOpen = false">
      <OwnerForm :initial="owner.data" :submitting="updateOwner.isPending" :errors="formErrors" @submit="onEdit" />
    </Modal>
  </template>
</template>
