import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import { createOwner, deleteOwner, fetchOwner, listOwners, updateOwner } from "../api/endpoints"
import type { OwnerCreate, OwnerUpdate } from "../api/types"

export function useOwners(search: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["owners", search.value.trim()]),
    queryFn: () => listOwners(search.value.trim() || undefined),
  })
}

export function useOwner(ownerId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["owner", ownerId.value]),
    queryFn: () => fetchOwner(ownerId.value),
    enabled: computed(() => Boolean(ownerId.value)),
  })
}

export function useCreateOwner() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: OwnerCreate) => createOwner(body),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["owners"] })
    },
  })
}

export function useUpdateOwner() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: { ownerId: string; body: OwnerUpdate }) =>
      updateOwner(input.ownerId, input.body),
    onSuccess: async (_data, input) => {
      await client.invalidateQueries({ queryKey: ["owners"] })
      await client.invalidateQueries({ queryKey: ["owner", input.ownerId] })
    },
  })
}

export function useDeleteOwner() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (ownerId: string) => deleteOwner(ownerId),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["owners"] })
    },
  })
}
