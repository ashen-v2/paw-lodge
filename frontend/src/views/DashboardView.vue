<script setup lang="ts">
import { computed, ref } from "vue"

import ErrorNotice from "../components/ErrorNotice.vue"
import PageHeader from "../components/PageHeader.vue"
import RevenueChart from "../components/RevenueChart.vue"
import SkeletonBlock from "../components/SkeletonBlock.vue"
import StatCard from "../components/StatCard.vue"
import { formatDate, greetingFor, isBeforeDay, thisMonthRange, utcToday } from "../lib/dates"
import { formatMoney } from "../lib/money"
import { presentQuery } from "../lib/present"
import { useDashboard, useRevenue, useServiceStats } from "../queries/useAnalytics"
import { usePets } from "../queries/usePets"
import { useMe } from "../queries/useSession"
import { useUpcoming } from "../queries/useVaccinations"
import { useVisits } from "../queries/useVisits"

const me = presentQuery(useMe())
const dashboard = presentQuery(useDashboard())
const visits = presentQuery(useVisits())
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const days = ref(30)
const upcoming = presentQuery(useUpcoming(days))
const range = computed(() => thisMonthRange())
const revenue = presentQuery(useRevenue(range))
const services = presentQuery(useServiceStats(range))

const greeting = computed(() => (me.data?.name ? greetingFor(me.data.name) : "Today at the clinic"))

const todayOutstanding = computed(() => {
  const today = utcToday()
  return (visits.data ?? [])
    .filter((visit) => visit.visit_date.slice(0, 10) === today)
    .reduce((sum, visit) => sum + Number(visit.outstanding), 0)
})

const petName = (id: string) => pets.data?.find((pet) => pet.id === id)?.name ?? "Pet"

const maxService = computed(() =>
  Math.max(1, ...(services.data ?? []).map((item) => Number(item.revenue))),
)
</script>

<template>
  <PageHeader
    :title="greeting"
    eyebrow="Clinic today"
    description="Today and this month follow UTC, which is how the server counts the day."
  >
    <template #actions>
      <RouterLink to="/app/visits/new" class="inline-flex min-h-11 items-center rounded-xl bg-leaf px-4 text-sm font-medium text-white">
        Record visit
      </RouterLink>
    </template>
  </PageHeader>

  <ErrorNotice v-if="dashboard.isError" :error="dashboard.error" @retry="dashboard.refetch()" />

  <section v-else aria-label="Today and this month" class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
    <template v-if="dashboard.isPending">
      <SkeletonBlock v-for="item in 6" :key="item" class-name="h-28" />
    </template>
    <template v-else-if="dashboard.data">
      <StatCard label="Visits today" :value="String(dashboard.data.today.visits)" detail="Counted by visit date" />
      <StatCard label="Revenue today" :value="formatMoney(dashboard.data.today.revenue)" detail="Payments received today" />
      <SkeletonBlock v-if="visits.isPending" class-name="h-28" />
      <StatCard
        v-else-if="visits.data"
        label="Unpaid today"
        :value="formatMoney(todayOutstanding)"
        detail="Unpaid balance on today's visits"
      />
      <StatCard v-else label="Unpaid today" value="—" detail="Could not load today's visits." />
      <SkeletonBlock v-if="pets.isPending" class-name="h-28" />
      <StatCard
        v-else-if="pets.data"
        label="Pets"
        :value="String(pets.data.length)"
        detail="On record"
      />
      <StatCard v-else label="Pets" value="—" detail="Could not load the pet list." />
      <StatCard label="New pets this month" :value="String(dashboard.data.month.new_pets)" />
      <StatCard label="Vaccinations this month" :value="String(dashboard.data.month.vaccinations)" detail="Given this month" />
    </template>
  </section>

  <section class="mt-6 grid gap-4 xl:grid-cols-5">
    <article class="rounded-2xl border border-line bg-card p-4 xl:col-span-3">
      <h2 class="font-serif text-2xl">Revenue this month</h2>
      <div v-if="revenue.isPending" class="mt-4">
        <SkeletonBlock class-name="h-56" />
      </div>
      <ErrorNotice v-else-if="revenue.isError" class="mt-4" :error="revenue.error" @retry="revenue.refetch()" />
      <div v-else class="mt-4">
        <RevenueChart :points="revenue.data ?? []" />
      </div>
    </article>

    <article class="rounded-2xl border border-line bg-card p-4 xl:col-span-2">
      <div class="flex items-baseline justify-between gap-3">
        <h2 class="font-serif text-2xl">Upcoming vaccines</h2>
        <p v-if="dashboard.data" class="text-sm text-muted">{{ dashboard.data.upcoming_vaccinations }} in 30 days</p>
      </div>
      <div v-if="upcoming.isPending" class="mt-4 grid gap-2">
        <SkeletonBlock class-name="h-16" />
        <SkeletonBlock class-name="h-16" />
      </div>
      <ErrorNotice v-else-if="upcoming.isError" class="mt-4" :error="upcoming.error" @retry="upcoming.refetch()" />
      <ul v-else-if="upcoming.data?.length" class="mt-4 divide-y divide-line">
        <li v-for="item in upcoming.data" :key="item.id" class="py-3">
          <RouterLink :to="`/app/pets/${item.pet_id}`" class="block min-h-11">
            <span class="font-medium">{{ petName(item.pet_id) }}</span>
            <span class="mt-1 block text-sm text-muted">
              {{ item.vaccine_name }} ·
              {{ isBeforeDay(item.next_due_date) ? "Overdue" : "Due" }}
              {{ formatDate(item.next_due_date) }}
            </span>
          </RouterLink>
        </li>
      </ul>
      <p v-else class="mt-4 text-sm text-muted">No vaccinations due in the next 30 days.</p>
      <RouterLink to="/app/vaccinations" class="mt-4 inline-flex min-h-11 items-center text-sm text-leaf underline-offset-2 hover:underline">
        Open vaccinations
      </RouterLink>
    </article>
  </section>

  <section class="mt-4 rounded-2xl border border-line bg-card p-4">
    <h2 class="font-serif text-2xl">Popular services this month</h2>
    <div v-if="services.isPending" class="mt-4 grid gap-3">
      <SkeletonBlock class-name="h-10" />
      <SkeletonBlock class-name="h-10" />
    </div>
    <ErrorNotice v-else-if="services.isError" class="mt-4" :error="services.error" @retry="services.refetch()" />
    <ul v-else-if="services.data?.length" class="mt-4 grid gap-3">
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
    <p v-else class="mt-4 text-sm text-muted">No services recorded this month.</p>
  </section>
</template>
