<script setup lang="ts">
import { ref } from "vue"

import type { TimelineEvent } from "../api/types"
import { formatDate, isBeforeDay } from "../lib/dates"
import { formatMoney } from "../lib/money"
import { methodLabel, visitPayStatus } from "../lib/status"
import Badge from "./Badge.vue"

defineProps<{ events: TimelineEvent[] }>()

const open = ref<Record<string, boolean>>({})

function eventKey(event: TimelineEvent, index: number): string {
  const id = detailString(event.details, "id")
  return id ?? `${event.type}-${event.date}-${index}`
}

function detailString(details: Record<string, unknown>, key: string): string | null {
  const value = details[key]
  return typeof value === "string" && value.trim() ? value : null
}

function detailNumber(details: Record<string, unknown>, key: string): number | null {
  const value = details[key]
  if (typeof value === "number" && Number.isFinite(value)) return value
  if (typeof value === "string" && value.trim() && Number.isFinite(Number(value))) return Number(value)
  return null
}

function detailItems(details: Record<string, unknown>): string[] {
  const value = details.items
  if (!Array.isArray(value)) return []
  return value.filter((item): item is string => typeof item === "string" && item.trim().length > 0)
}

function typeLabel(type: TimelineEvent["type"]): string {
  if (type === "visit") return "Visit"
  if (type === "vaccination") return "Vaccination"
  return "Payment"
}

function toggle(key: string) {
  open.value = { ...open.value, [key]: !open.value[key] }
}

function visitHref(event: TimelineEvent): string | null {
  if (event.type === "visit") {
    const id = detailString(event.details, "id")
    return id ? `/app/visits/${id}` : null
  }
  if (event.type === "payment") {
    const id = detailString(event.details, "visit_id")
    return id ? `/app/visits/${id}` : null
  }
  return null
}

function historyPay(event: TimelineEvent): { tone: "ok" | "warn" | "danger"; label: string } {
  const total = detailNumber(event.details, "total") ?? 0
  const outstanding = detailNumber(event.details, "outstanding") ?? 0
  if (outstanding <= 0.009) return visitPayStatus(0, true)
  if (outstanding < total - 0.009) return visitPayStatus(outstanding, true)
  return visitPayStatus(outstanding, false)
}

function dueText(event: TimelineEvent): string | null {
  const due = detailString(event.details, "next_due_date")
  if (!due) return null
  return isBeforeDay(due) ? `Overdue · due ${formatDate(due)}` : `Due ${formatDate(due)}`
}
</script>

<template>
  <ol v-if="events.length" class="grid gap-3">
    <li v-for="(event, index) in events" :key="eventKey(event, index)" class="rounded-2xl border border-line bg-card">
      <button
        type="button"
        class="flex w-full items-start gap-3 px-4 py-3 text-left"
        :aria-expanded="Boolean(open[eventKey(event, index)])"
        @click="toggle(eventKey(event, index))"
      >
        <span class="mt-0.5 w-24 shrink-0 text-sm text-muted">{{ formatDate(event.date) }}</span>
        <span class="min-w-0 flex-1">
          <span class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-medium uppercase tracking-wide text-muted">{{ typeLabel(event.type) }}</span>
            <Badge v-if="event.type === 'visit'" :tone="historyPay(event).tone">
              {{ historyPay(event).label }}
            </Badge>
            <Badge
              v-else-if="event.type === 'vaccination' && dueText(event)"
              :tone="dueText(event)?.startsWith('Overdue') ? 'danger' : 'warn'"
            >
              {{ dueText(event) }}
            </Badge>
            <Badge v-else-if="event.type === 'payment'" tone="ok">Paid</Badge>
          </span>
          <span class="mt-1 block font-medium text-ink">{{ event.title }}</span>
          <span v-if="event.type === 'visit' && detailNumber(event.details, 'total') !== null" class="mt-1 block text-sm text-muted">
            {{ formatMoney(detailNumber(event.details, "total")) }}
            <template v-if="(detailNumber(event.details, 'outstanding') ?? 0) > 0.009">
              · {{ formatMoney(detailNumber(event.details, "outstanding")) }} outstanding
            </template>
          </span>
          <span v-else-if="event.type === 'payment' && detailNumber(event.details, 'amount') !== null" class="mt-1 block text-sm text-muted">
            {{ formatMoney(detailNumber(event.details, "amount")) }}
            · {{ methodLabel(detailString(event.details, "payment_method") ?? "other") }}
          </span>
        </span>
        <span class="shrink-0 text-sm text-leaf">{{ open[eventKey(event, index)] ? "Hide" : "Details" }}</span>
      </button>
      <div v-if="open[eventKey(event, index)]" class="border-t border-line px-4 py-3 text-sm">
        <p v-if="detailString(event.details, 'notes')" class="text-ink">{{ detailString(event.details, "notes") }}</p>
        <ul v-if="detailItems(event.details).length" class="mt-2 list-disc pl-5 text-muted">
          <li v-for="item in detailItems(event.details)" :key="item">{{ item }}</li>
        </ul>
        <p v-if="detailString(event.details, 'batch_number')" class="mt-2 text-muted">
          Batch {{ detailString(event.details, "batch_number") }}
        </p>
        <RouterLink
          v-if="visitHref(event)"
          :to="visitHref(event) || '/app/visits'"
          class="mt-3 inline-flex min-h-11 items-center text-leaf underline-offset-2 hover:underline"
        >
          Open visit
        </RouterLink>
      </div>
    </li>
  </ol>
  <p v-else class="rounded-2xl border border-dashed border-line bg-card px-4 py-8 text-center text-sm text-muted">
    No visits, vaccinations, or payments yet.
  </p>
</template>
