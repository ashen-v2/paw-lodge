<script setup lang="ts">
import { computed, ref } from "vue"

import ErrorNotice from "../components/ErrorNotice.vue"
import PageHeader from "../components/PageHeader.vue"
import RevenueChart from "../components/RevenueChart.vue"
import StatCard from "../components/StatCard.vue"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import { lastDaysRange, lastMonthRange, thisMonthRange, utcToday, type DateRange } from "../lib/dates"
import { formatMoney } from "../lib/money"
import { presentQuery } from "../lib/present"
import { useDashboard, useRevenue, useServiceStats } from "../queries/useAnalytics"

type Preset = "today" | "7" | "month" | "last" | "custom"

const preset = ref<Preset>("month")
const customFrom = ref(thisMonthRange().from)
const customTo = ref(utcToday())

const range = computed<DateRange>(() => {
  if (preset.value === "today") return { from: utcToday(), to: utcToday() }
  if (preset.value === "7") return lastDaysRange(7)
  if (preset.value === "last") return lastMonthRange()
  if (preset.value === "custom") return { from: customFrom.value, to: customTo.value }
  return thisMonthRange()
})

const rangeValid = computed(() => Boolean(range.value.from && range.value.to && range.value.from <= range.value.to))
const revenue = presentQuery(useRevenue(range, rangeValid))
const services = presentQuery(useServiceStats(range, rangeValid))
const dashboard = presentQuery(useDashboard())

const total = computed(() =>
  (revenue.data ?? []).reduce((sum, point) => sum + Number(point.revenue), 0),
)

const maxService = computed(() =>
  Math.max(1, ...(services.data ?? []).map((item) => Number(item.revenue))),
)

const presets: { id: Preset; label: string }[] = [
  { id: "today", label: "Today" },
  { id: "7", label: "7 days" },
  { id: "month", label: "This month" },
  { id: "last", label: "Last month" },
  { id: "custom", label: "Custom" },
]
</script>

<template>
  <PageHeader
    title="Analytics"
    description="Revenue and service totals follow the range. Visit, new pet, and vaccination counts are this month only — that is what the clinic summary returns."
  />

  <div class="mb-4 flex flex-wrap gap-2" role="group" aria-label="Date range">
    <AppButton
      v-for="item in presets"
      :key="item.id"
      type="button"
      :variant="preset === item.id ? 'primary' : 'secondary'"
      @click="preset = item.id"
    >
      {{ item.label }}
    </AppButton>
  </div>

  <div v-if="preset === 'custom'" class="mb-4 grid gap-3 sm:grid-cols-2">
    <AppField label="From" field-id="analytics-from" :error="rangeValid ? undefined : 'Start date must be on or before the end date.'">
      <AppInput id="analytics-from" v-model="customFrom" type="date" :invalid="!rangeValid" />
    </AppField>
    <AppField label="To" field-id="analytics-to">
      <AppInput id="analytics-to" v-model="customTo" type="date" />
    </AppField>
  </div>

  <section aria-label="This month" class="grid gap-3 md:grid-cols-3">
    <StatCard
      v-if="dashboard.data"
      label="Visits this month"
      :value="String(dashboard.data.month.visits)"
      detail="UTC month, not the chart range"
    />
    <StatCard
      v-if="dashboard.data"
      label="New pets this month"
      :value="String(dashboard.data.month.new_pets)"
      detail="UTC month, not the chart range"
    />
    <StatCard
      v-if="dashboard.data"
      label="Vaccinations this month"
      :value="String(dashboard.data.month.vaccinations)"
      detail="UTC month, not the chart range"
    />
  </section>
  <ErrorNotice v-if="dashboard.isError" class="mt-3" :error="dashboard.error" @retry="dashboard.refetch()" />

  <article class="mt-4 rounded-2xl border border-line bg-card p-4">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 class="font-serif text-2xl">Revenue</h2>
      <p v-if="revenue.data" class="text-sm tabular-nums text-muted">{{ formatMoney(total) }} in this range</p>
    </div>
    <ErrorNotice v-if="revenue.isError" class="mt-4" :error="revenue.error" @retry="revenue.refetch()" />
    <div v-else-if="rangeValid" class="mt-4">
      <RevenueChart :points="revenue.data ?? []" />
    </div>
  </article>

  <article class="mt-4 rounded-2xl border border-line bg-card p-4">
    <h2 class="font-serif text-2xl">Services</h2>
    <ErrorNotice v-if="services.isError" class="mt-4" :error="services.error" @retry="services.refetch()" />
    <p v-else-if="services.data && !services.data.length" class="mt-4 text-sm text-muted">No services in this range.</p>
    <ul v-else class="mt-4 grid gap-3">
      <li v-for="item in services.data" :key="item.service">
        <div class="flex items-baseline justify-between gap-3 text-sm">
          <span class="min-w-0 truncate">{{ item.service }}</span>
          <span class="shrink-0 tabular-nums">{{ item.count }} · {{ formatMoney(item.revenue) }}</span>
        </div>
        <div
          class="mt-1 h-2 rounded-full bg-paper"
          role="img"
          :aria-label="`${item.service}, ${item.count} times, ${formatMoney(item.revenue)}`"
        >
          <div
            class="h-2 rounded-full bg-leaf"
            :style="{ width: `${Math.max(4, (Number(item.revenue) / maxService) * 100)}%` }"
          />
        </div>
      </li>
    </ul>
  </article>
</template>
