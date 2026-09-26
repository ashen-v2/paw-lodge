import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"

import { createService, deactivateService, listServices, updateService } from "../api/endpoints"
import type { ServiceCreate, ServiceUpdate } from "../api/types"

export function useServices(includeInactive: Ref<boolean>) {
  return useQuery({
    queryKey: computed(() => ["services", includeInactive.value]),
    queryFn: () => listServices(includeInactive.value),
  })
}

export function useCreateService() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: ServiceCreate) => createService(body),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["services"] })
    },
  })
}

export function useUpdateService() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: { serviceId: string; body: ServiceUpdate }) =>
      updateService(input.serviceId, input.body),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["services"] })
    },
  })
}

export function useDeactivateService() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (serviceId: string) => deactivateService(serviceId),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["services"] })
    },
  })
}
