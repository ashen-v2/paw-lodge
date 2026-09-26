import { useQuery } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import { fetchDashboard, fetchRevenue, fetchServiceStats } from "../api/endpoints"
import type { DateRange } from "../lib/dates"

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  })
}

export function useRevenue(range: Ref<DateRange>, enabled?: Ref<boolean>) {
  return useQuery({
    queryKey: computed(() => ["revenue", range.value.from, range.value.to]),
    queryFn: () => fetchRevenue(range.value.from, range.value.to),
    enabled: () => enabled?.value ?? true,
  })
}

export function useServiceStats(range: Ref<DateRange>, enabled?: Ref<boolean>) {
  return useQuery({
    queryKey: computed(() => ["service-stats", range.value.from, range.value.to]),
    queryFn: () => fetchServiceStats(range.value.from, range.value.to),
    enabled: () => enabled?.value ?? true,
  })
}
