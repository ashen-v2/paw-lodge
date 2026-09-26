import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import {
  createPet,
  deletePet,
  fetchPet,
  fetchPetHistory,
  fetchPetVaccinations,
  fetchPetVisits,
  listPets,
  updatePet,
} from "../api/endpoints"
import type { PetCreate, PetUpdate } from "../api/types"

export function usePets(search: Ref<string>, species: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["pets", search.value.trim(), species.value.trim()]),
    queryFn: () => listPets(search.value.trim() || undefined, species.value.trim() || undefined),
  })
}

export function usePet(petId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["pet", petId.value]),
    queryFn: () => fetchPet(petId.value),
    enabled: computed(() => Boolean(petId.value)),
  })
}

export function usePetHistory(petId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["pet-history", petId.value]),
    queryFn: () => fetchPetHistory(petId.value),
    enabled: computed(() => Boolean(petId.value)),
  })
}

export function usePetVisits(petId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["pet-visits", petId.value]),
    queryFn: () => fetchPetVisits(petId.value),
    enabled: computed(() => Boolean(petId.value)),
  })
}

export function usePetVaccinations(petId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["pet-vaccinations", petId.value]),
    queryFn: () => fetchPetVaccinations(petId.value),
    enabled: computed(() => Boolean(petId.value)),
  })
}

export function useCreatePet() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: PetCreate) => createPet(body),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["pets"] })
      await client.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useUpdatePet() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: { petId: string; body: PetUpdate }) => updatePet(input.petId, input.body),
    onSuccess: async (_data, input) => {
      await client.invalidateQueries({ queryKey: ["pets"] })
      await client.invalidateQueries({ queryKey: ["pet", input.petId] })
      await client.invalidateQueries({ queryKey: ["pet-history", input.petId] })
    },
  })
}

export function useDeletePet() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (petId: string) => deletePet(petId),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["pets"] })
      await client.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}
