<script setup lang="ts">
import { computed, ref } from "vue"

import AppButton from "../components/AppButton.vue"
import Badge from "../components/Badge.vue"
import DataTable from "../components/DataTable.vue"
import EmptyState from "../components/EmptyState.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import MobileList from "../components/MobileList.vue"
import PageHeader from "../components/PageHeader.vue"
import SearchInput from "../components/SearchInput.vue"
import { formatDate } from "../lib/dates"
import { formatMoney } from "../lib/money"
import { presentQuery } from "../lib/present"
import { visitPayStatus } from "../lib/status"
import { usePets } from "../queries/usePets"
import { useVisits } from "../queries/useVisits"

const visits = presentQuery(useVisits())
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const filter = ref("")

const petName = (id: string) => pets.data?.find((pet) => pet.id === id)?.name ?? "Pet"

const filtered = computed(() => {
  const query = filter.value.trim().toLowerCase()
  const rows = visits.data ?? []
  if (!query) return rows
  return rows.filter((visit) => {
    const name = petName(visit.pet_id).toLowerCase()
    const diagnosis = (visit.diagnosis ?? "").toLowerCase()
    return name.includes(query) || diagnosis.includes(query)
  })
})
</script>

<template>
  <PageHeader title="Visits" description="Every visit recorded for this clinic.">
    <template #actions>
      <RouterLink to="/app/visits/new" class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white">
        Record visit
      </RouterLink>
    </template>
  </PageHeader>

  <div class="mb-4 max-w-md">
    <SearchInput id="visit-filter" v-model="filter" label="Search by pet or diagnosis" />
  </div>

  <ErrorNotice v-if="visits.isError" :error="visits.error" @retry="visits.refetch()" />
  <EmptyState v-else-if="visits.data && !visits.data.length" title="No visits yet" body="Record a visit when a pet is seen.">
    <RouterLink to="/app/visits/new" class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white">
      Record visit
    </RouterLink>
  </EmptyState>
  <EmptyState v-else-if="visits.data && !filtered.length" title="No visits match" body="Try another pet name or diagnosis.">
    <AppButton variant="secondary" @click="filter = ''">Clear search</AppButton>
  </EmptyState>
  <template v-else-if="filtered.length">
    <DataTable>
      <thead class="bg-paper text-muted">
        <tr>
          <th class="px-4 py-3 font-medium" scope="col">Date</th>
          <th class="px-4 py-3 font-medium" scope="col">Pet</th>
          <th class="px-4 py-3 font-medium" scope="col">Diagnosis</th>
          <th class="px-4 py-3 font-medium" scope="col">Total</th>
          <th class="px-4 py-3 font-medium" scope="col">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="visit in filtered" :key="visit.id" class="border-t border-line">
          <td class="px-4 py-3">
            <RouterLink :to="`/app/visits/${visit.id}`" class="font-medium text-leaf underline-offset-2 hover:underline">
              {{ formatDate(visit.visit_date) }}
            </RouterLink>
          </td>
          <td class="px-4 py-3">{{ petName(visit.pet_id) }}</td>
          <td class="px-4 py-3">{{ visit.diagnosis || "Visit" }}</td>
          <td class="px-4 py-3 tabular-nums">{{ formatMoney(visit.total) }}</td>
          <td class="px-4 py-3">
            <Badge :tone="visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).tone">
              {{ visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).label }}
            </Badge>
          </td>
        </tr>
      </tbody>
    </DataTable>
    <MobileList>
      <RouterLink
        v-for="visit in filtered"
        :key="visit.id"
        :to="`/app/visits/${visit.id}`"
        class="block rounded-2xl border border-line bg-card p-4"
      >
        <span class="flex items-start justify-between gap-3">
          <span>
            <span class="block font-medium">{{ petName(visit.pet_id) }}</span>
            <span class="mt-1 block text-sm text-muted">{{ formatDate(visit.visit_date) }} · {{ visit.diagnosis || "Visit" }}</span>
          </span>
          <Badge :tone="visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).tone">
            {{ visitPayStatus(Number(visit.outstanding), Boolean(visit.payment)).label }}
          </Badge>
        </span>
        <span class="mt-2 block text-sm tabular-nums">{{ formatMoney(visit.total) }}</span>
      </RouterLink>
    </MobileList>
  </template>
</template>
