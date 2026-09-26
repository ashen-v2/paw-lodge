<script setup lang="ts">
import { ref } from "vue"

import { ApiError, errorMessage } from "../api/errors"
import type { Service } from "../api/types"
import AppButton from "../components/AppButton.vue"
import Badge from "../components/Badge.vue"
import DataTable from "../components/DataTable.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import MobileList from "../components/MobileList.vue"
import Modal from "../components/Modal.vue"
import PageHeader from "../components/PageHeader.vue"
import ServiceForm from "../components/ServiceForm.vue"
import SkeletonBlock from "../components/SkeletonBlock.vue"
import { askConfirm } from "../lib/confirm"
import { blankToNull } from "../lib/form"
import { formatMoney } from "../lib/money"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { useCreateService, useDeactivateService, useServices, useUpdateService } from "../queries/useServices"

const includeInactive = ref(false)
const services = presentQuery(useServices(includeInactive))
const createService = presentMutation(useCreateService())
const updateService = presentMutation(useUpdateService())
const deactivate = presentMutation(useDeactivateService())

const formOpen = ref(false)
const editing = ref<Service | null>(null)
const formErrors = ref<Record<string, string>>({})

function openCreate() {
  editing.value = null
  formErrors.value = {}
  formOpen.value = true
}

function openEdit(service: Service) {
  editing.value = service
  formErrors.value = {}
  formOpen.value = true
}

async function onSubmit(value: { name: string; description: string; price: string; is_active: boolean }) {
  formErrors.value = {}
  if (editing.value?.is_active && !value.is_active) {
    const ok = await askConfirm({
      title: `Deactivate ${editing.value.name}?`,
      message: "It will stay on old visits, and it will not appear when recording a new visit.",
      confirmLabel: "Deactivate",
    })
    if (!ok) return
  }
  const body = {
    name: value.name,
    description: blankToNull(value.description),
    price: value.price,
    is_active: value.is_active,
  }
  try {
    if (editing.value) {
      await updateService.mutateAsync({ serviceId: editing.value.id, body })
      toast.success("Service updated.")
    } else {
      await createService.mutateAsync(body)
      toast.success("Service added.")
    }
    formOpen.value = false
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) formErrors.value = error.fields
    else toast.error(errorMessage(error))
  }
}

async function onDeactivate(service: Service) {
  const ok = await askConfirm({
    title: `Deactivate ${service.name}?`,
    message: "It will stay on old visits, and it will not appear when recording a new visit.",
    confirmLabel: "Deactivate",
  })
  if (!ok) return
  try {
    await deactivate.mutateAsync(service.id)
    toast.success(`${service.name} is inactive.`)
  } catch (error) {
    toast.error(errorMessage(error))
  }
}
</script>

<template>
  <PageHeader title="Services" description="Prices are copied onto a visit when you record it. Later changes do not rewrite old bills.">
    <template #actions>
      <AppButton @click="openCreate">Add service</AppButton>
    </template>
  </PageHeader>

  <label class="mb-4 flex min-h-11 items-center gap-3 text-sm">
    <input v-model="includeInactive" type="checkbox" class="size-5 accent-leaf" />
    Show inactive
  </label>

  <ErrorNotice v-if="services.isError" :error="services.error" @retry="services.refetch()" />
  <div v-else-if="services.isPending" class="grid gap-3">
    <SkeletonBlock class-name="h-20" />
    <SkeletonBlock class-name="h-20" />
    <SkeletonBlock class-name="h-20" />
  </div>
  <EmptyState
    v-else-if="!services.data?.length"
    title="No services yet"
    body="Add the treatments you charge for, then pick them on a visit."
  >
    <AppButton @click="openCreate">Add service</AppButton>
  </EmptyState>
  <template v-else>
    <DataTable>
      <thead class="bg-paper text-muted">
        <tr>
          <th class="px-4 py-3 font-medium" scope="col">Name</th>
          <th class="px-4 py-3 font-medium" scope="col">Price</th>
          <th class="px-4 py-3 font-medium" scope="col">Status</th>
          <th class="px-4 py-3 font-medium" scope="col"><span class="sr-only">Actions</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="service in services.data" :key="service.id" class="border-t border-line">
          <td class="px-4 py-3">
            <p class="font-medium">{{ service.name }}</p>
            <p v-if="service.description" class="text-muted">{{ service.description }}</p>
          </td>
          <td class="px-4 py-3 tabular-nums">{{ formatMoney(service.price) }}</td>
          <td class="px-4 py-3">
            <Badge :tone="service.is_active ? 'ok' : 'neutral'">{{ service.is_active ? "Active" : "Inactive" }}</Badge>
          </td>
          <td class="px-4 py-3">
            <div class="flex flex-wrap gap-2">
              <AppButton variant="secondary" @click="openEdit(service)">Edit</AppButton>
              <AppButton v-if="service.is_active" variant="ghost" @click="onDeactivate(service)">Deactivate</AppButton>
            </div>
          </td>
        </tr>
      </tbody>
    </DataTable>
    <MobileList>
      <article v-for="service in services.data" :key="service.id" class="rounded-2xl border border-line bg-card p-4">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="font-medium">{{ service.name }}</p>
            <p class="mt-1 text-sm tabular-nums">{{ formatMoney(service.price) }}</p>
            <p v-if="service.description" class="mt-1 text-sm text-muted">{{ service.description }}</p>
          </div>
          <Badge :tone="service.is_active ? 'ok' : 'neutral'">{{ service.is_active ? "Active" : "Inactive" }}</Badge>
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <AppButton variant="secondary" @click="openEdit(service)">Edit</AppButton>
          <AppButton v-if="service.is_active" variant="ghost" @click="onDeactivate(service)">Deactivate</AppButton>
        </div>
      </article>
    </MobileList>
  </template>

  <Modal :open="formOpen" :title="editing ? 'Edit service' : 'Add service'" @close="formOpen = false">
    <ServiceForm
      :key="editing?.id ?? 'new'"
      :initial="editing"
      :submitting="createService.isPending || updateService.isPending"
      :errors="formErrors"
      @submit="onSubmit"
    />
  </Modal>
</template>
