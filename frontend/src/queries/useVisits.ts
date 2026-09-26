import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import { createPayment, createVisit, deleteVisit, fetchVisit, listVisits } from "../api/endpoints"
import type { PaymentCreate, VisitCreate } from "../api/types"

async function refreshVisit(client: ReturnType<typeof useQueryClient>, petId?: string) {
  await client.invalidateQueries({ queryKey: ["visits"] })
  await client.invalidateQueries({ queryKey: ["visit"] })
  await client.invalidateQueries({ queryKey: ["dashboard"] })
  await client.invalidateQueries({ queryKey: ["revenue"] })
  await client.invalidateQueries({ queryKey: ["service-stats"] })
  await client.invalidateQueries({ queryKey: ["pet-history"] })
  await client.invalidateQueries({ queryKey: ["pet-visits"] })
  if (petId) {
    await client.invalidateQueries({ queryKey: ["pet", petId] })
  }
}

export function useVisits() {
  return useQuery({
    queryKey: ["visits"],
    queryFn: listVisits,
  })
}

export function useVisit(visitId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["visit", visitId.value]),
    queryFn: () => fetchVisit(visitId.value),
    enabled: computed(() => Boolean(visitId.value)),
  })
}

export function useCreateVisit() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: VisitCreate) => createVisit(body),
    onSuccess: async (visit) => {
      await refreshVisit(client, visit.pet_id)
    },
  })
}

export function useDeleteVisit() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: { visitId: string; petId: string }) => deleteVisit(input.visitId),
    onSuccess: async (_data, input) => {
      await refreshVisit(client, input.petId)
    },
  })
}

export function useCreatePayment() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: PaymentCreate) => createPayment(body),
    onSuccess: async (payment) => {
      await client.invalidateQueries({ queryKey: ["visit", payment.visit_id] })
      await refreshVisit(client)
    },
  })
}
