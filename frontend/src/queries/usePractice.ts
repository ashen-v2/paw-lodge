import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"

import { fetchPractice, updatePractice } from "../api/endpoints"
import type { PracticeUpdate } from "../api/types"

export function usePractice() {
  return useQuery({
    queryKey: ["practice"],
    queryFn: fetchPractice,
  })
}

export function useUpdatePractice() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (body: PracticeUpdate) => updatePractice(body),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["practice"] })
    },
  })
}
