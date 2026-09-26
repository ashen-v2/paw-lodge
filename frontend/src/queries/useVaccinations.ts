import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import { createVaccination, deleteVaccination, listUpcomingVaccinations, listVaccinations } from "../api/endpoints"
import type { VaccinationCreate } from "../api/types"

async function refreshVaccines(client: ReturnType<typeof useQueryClient>, petId?: string) {
  await client.invalidateQueries({ queryKey: ["vaccinations"] })
  await client.invalidateQueries({ queryKey: ["upcoming"] })
  await client.invalidateQueries({ queryKey: ["dashboard"] })
  if (petId) {
    await client.invalidateQueries({ queryKey: ["pet-vaccinations", petId] })
    await client.invalidateQueries({ queryKey: ["pet-history", petId] })
  }
}

export function useVaccinations() {
  return useQuery({
    queryKey: ["vaccinations"],
    queryFn: listVaccinations,
  })
}

export function useUpcoming(days: Ref<number>) {
  return useQuery({
    queryKey: computed(() => ["upcoming", days.value]),
    queryFn: () => listUpcomingVaccinations(days.value),
  })
}

export function useCreateVaccination() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: VaccinationCreate) => createVaccination(body),
    onSuccess: async (record) => {
      await refreshVaccines(client, record.pet_id)
    },
  })
}

export function useDeleteVaccination() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: { vaccinationId: string; petId: string }) =>
      deleteVaccination(input.vaccinationId),
    onSuccess: async (_data, input) => {
      await refreshVaccines(client, input.petId)
    },
  })
}
