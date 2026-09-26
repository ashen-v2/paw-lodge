<script setup lang="ts">
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import type { Service, VisitItemCreate } from "../api/types"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import AppSelect from "../components/AppSelect.vue"
import AppTextarea from "../components/AppTextarea.vue"
import Breadcrumb from "../components/Breadcrumb.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import PageHeader from "../components/PageHeader.vue"
import SearchInput from "../components/SearchInput.vue"
import { utcToday } from "../lib/dates"
import { blankToNull } from "../lib/form"
import { formatMoney, lineAmount } from "../lib/money"
import { presentMutation, presentQuery } from "../lib/present"
import { toast } from "../lib/toast"
import { usePets } from "../queries/usePets"
import { useServices } from "../queries/useServices"
import { useCreateVisit } from "../queries/useVisits"

type DraftLine = {
  key: number
  serviceId: string | null
  description: string
  quantity: string
  unitPrice: string
}

const route = useRoute()
const router = useRouter()
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const includeInactive = ref(false)
const services = presentQuery(useServices(includeInactive))
const createVisit = presentMutation(useCreateVisit())

const petId = ref(typeof route.query.pet === "string" ? route.query.pet : "")
const visitDate = ref(utcToday())
const diagnosis = ref("")
const notes = ref("")
const followUp = ref("")
const serviceQuery = ref("")
const lines = ref<DraftLine[]>([])
const oneOffName = ref("")
const oneOffPrice = ref("")
const oneOffError = ref("")
const formError = ref("")
let nextKey = 1

const activeServices = computed(() =>
  (services.data ?? []).filter((service) => {
    const query = serviceQuery.value.trim().toLowerCase()
    if (!query) return true
    return service.name.toLowerCase().includes(query)
  }),
)

const visibleServices = computed(() => activeServices.value.slice(0, serviceQuery.value.trim() ? 8 : 6))

const estimate = computed(() =>
  Math.round(
    lines.value.reduce((sum, line) => {
      const quantity = Number(line.quantity)
      const price = Number(line.unitPrice)
      if (!Number.isFinite(quantity) || !Number.isFinite(price)) return sum
      return sum + lineAmount(quantity, price)
    }, 0) * 100,
  ) / 100,
)

function addService(service: Service) {
  const existing = lines.value.find((line) => line.serviceId === service.id)
  if (existing) {
    existing.quantity = String((Number(existing.quantity) || 1) + 1)
    return
  }
  lines.value.push({
    key: nextKey++,
    serviceId: service.id,
    description: service.name,
    quantity: "1",
    unitPrice: String(service.price),
  })
}

function addOneOff() {
  oneOffError.value = ""
  if (!oneOffName.value.trim()) {
    oneOffError.value = "Enter a description."
    return
  }
  const raw = String(oneOffPrice.value ?? "").trim()
  const price = Number(raw)
  if (raw === "" || !Number.isFinite(price) || price < 0) {
    oneOffError.value = "Enter a price of zero or more."
    return
  }
  lines.value.push({
    key: nextKey++,
    serviceId: null,
    description: oneOffName.value.trim(),
    quantity: "1",
    unitPrice: price.toFixed(2),
  })
  oneOffName.value = ""
  oneOffPrice.value = ""
}

function changeQty(line: DraftLine, delta: number) {
  const next = (Number(line.quantity) || 1) + delta
  line.quantity = String(Math.max(1, next))
}

async function onSubmit() {
  formError.value = ""
  if (!petId.value) {
    formError.value = "Choose a pet."
    return
  }
  if (!visitDate.value) {
    formError.value = "Enter the visit date."
    return
  }
  for (const line of lines.value) {
    const quantity = Number(line.quantity)
    if (!Number.isInteger(quantity) || quantity < 1) {
      formError.value = "Each treatment needs a quantity of at least 1."
      return
    }
  }
  const items: VisitItemCreate[] = lines.value.map((line) => {
    if (line.serviceId) return { service_id: line.serviceId, quantity: Number(line.quantity) }
    return {
      description: line.description,
      quantity: Number(line.quantity),
      unit_price: line.unitPrice,
    }
  })
  try {
    const visit = await createVisit.mutateAsync({
      pet_id: petId.value,
      visit_date: visitDate.value,
      diagnosis: blankToNull(diagnosis.value),
      notes: blankToNull(notes.value),
      follow_up_date: followUp.value || null,
      items,
    })
    toast.success(`Visit saved. Total ${formatMoney(visit.total)}.`)
    await router.push(`/app/visits/${visit.id}`)
  } catch (error) {
    formError.value = error instanceof ApiError ? error.message : errorMessage(error)
  }
}
</script>

<template>
  <Breadcrumb :items="[{ label: 'Visits', to: '/app/visits' }, { label: 'Record visit' }]" />
  <PageHeader title="Record visit" description="The total you see here is an estimate. The saved visit uses the server total." />

  <ErrorNotice v-if="pets.isError" :error="pets.error" @retry="pets.refetch()" />
  <EmptyState
    v-else-if="pets.data && pets.data.length === 0"
    title="Add a pet first"
    body="A visit has to belong to a pet."
  >
    <RouterLink to="/app/pets" class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white">
      Go to pets
    </RouterLink>
  </EmptyState>

  <form v-else class="pb-16 lg:pb-0" @submit.prevent="onSubmit">
    <p v-if="formError" class="mb-4 rounded-xl bg-danger-bg px-3 py-2 text-sm text-danger" role="alert">{{ formError }}</p>
    <div class="grid gap-6 lg:grid-cols-2">
      <section class="grid gap-4 rounded-2xl border border-line bg-card p-4">
        <h2 class="font-serif text-2xl">Visit</h2>
        <AppField label="Pet" field-id="visit-pet">
          <AppSelect id="visit-pet" v-model="petId">
            <option value="">Choose a pet</option>
            <option v-for="pet in pets.data" :key="pet.id" :value="pet.id">{{ pet.name }} · {{ pet.species }}</option>
          </AppSelect>
        </AppField>
        <AppField label="Date" field-id="visit-date">
          <AppInput id="visit-date" v-model="visitDate" type="date" />
        </AppField>
        <AppField label="Diagnosis" field-id="visit-diagnosis" hint="Shown as the title in the pet’s history.">
          <AppInput id="visit-diagnosis" v-model="diagnosis" maxlength="255" />
        </AppField>
        <AppField label="Notes" field-id="visit-notes" hint="Optional.">
          <AppTextarea id="visit-notes" v-model="notes" :rows="4" />
        </AppField>
        <AppField label="Follow-up" field-id="visit-follow" hint="Optional.">
          <AppInput id="visit-follow" v-model="followUp" type="date" />
        </AppField>
      </section>

      <section class="rounded-2xl border border-line bg-card p-4">
        <h2 class="font-serif text-2xl">Treatments</h2>
        <div class="mt-4">
          <SearchInput id="service-search" v-model="serviceQuery" label="Find a service" />
        </div>
        <ErrorNotice v-if="services.isError" class="mt-3" :error="services.error" @retry="services.refetch()" />
        <p v-else-if="services.data && services.data.length === 0" class="mt-3 text-sm text-muted">
          No active services.
          <RouterLink to="/app/services" class="text-leaf underline-offset-2 hover:underline">Add a service</RouterLink>
          or use a one-off item.
        </p>
        <ul v-else class="mt-3 divide-y divide-line">
          <li v-for="service in visibleServices" :key="service.id">
            <button
              type="button"
              class="flex min-h-11 w-full items-center justify-between gap-3 text-left text-sm"
              @click="addService(service)"
            >
              <span>{{ service.name }}</span>
              <span class="shrink-0 tabular-nums text-muted">{{ formatMoney(service.price) }}</span>
            </button>
          </li>
        </ul>

        <div class="mt-4 grid gap-3 rounded-xl bg-paper p-3">
          <p class="text-sm font-medium">One-off item</p>
          <AppField label="Description" field-id="one-off-name" :error="oneOffError">
            <AppInput id="one-off-name" v-model="oneOffName" maxlength="255" :invalid="Boolean(oneOffError)" />
          </AppField>
          <AppField label="Price" field-id="one-off-price">
            <AppInput id="one-off-price" v-model="oneOffPrice" type="number" min="0" step="0.01" inputmode="decimal" />
          </AppField>
          <AppButton type="button" variant="secondary" @click="addOneOff">Add one-off item</AppButton>
        </div>

        <h3 class="mt-5 text-sm font-medium">Selected</h3>
        <p v-if="lines.length === 0" class="mt-2 text-sm text-muted">No treatments yet. The visit can still be saved.</p>
        <ul v-else class="mt-2 grid gap-3">
          <li v-for="line in lines" :key="line.key" class="rounded-xl border border-line p-3">
            <div class="flex items-start justify-between gap-3">
              <p class="font-medium">{{ line.description }}</p>
              <button type="button" class="min-h-11 shrink-0 text-sm text-danger" @click="lines = lines.filter((item) => item.key !== line.key)">
                Remove
              </button>
            </div>
            <p class="text-sm text-muted">{{ line.serviceId ? "Catalog price" : "One-off" }} · {{ formatMoney(line.unitPrice) }}</p>
            <div class="mt-2 flex items-center gap-2">
              <button type="button" class="min-h-11 min-w-11 rounded-xl border border-line" aria-label="Decrease quantity" @click="changeQty(line, -1)">
                −
              </button>
              <AppInput
                :id="`qty-${line.key}`"
                v-model="line.quantity"
                type="number"
                min="1"
                step="1"
                class="max-w-24"
                :aria-label="`Quantity for ${line.description}`"
              />
              <button type="button" class="min-h-11 min-w-11 rounded-xl border border-line" aria-label="Increase quantity" @click="changeQty(line, 1)">
                +
              </button>
              <span class="ml-auto text-sm tabular-nums">{{ formatMoney(lineAmount(Number(line.quantity) || 0, Number(line.unitPrice) || 0)) }}</span>
            </div>
          </li>
        </ul>
        <p class="mt-4 text-sm text-muted" aria-live="polite">Estimated total {{ formatMoney(estimate) }}</p>
      </section>
    </div>

    <div
      class="fixed inset-x-0 z-30 border-t border-line bg-card px-4 py-3 lg:static lg:mt-6 lg:border-0 lg:bg-transparent lg:px-0"
      style="bottom: calc(4.25rem + env(safe-area-inset-bottom))"
    >
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-3">
        <div>
          <p class="text-xs text-muted">Estimated total</p>
          <p class="font-serif text-2xl tabular-nums">{{ formatMoney(estimate) }}</p>
        </div>
        <AppButton type="submit" :disabled="createVisit.isPending">
          {{ createVisit.isPending ? "Saving…" : "Save visit" }}
        </AppButton>
      </div>
    </div>
  </form>
</template>
