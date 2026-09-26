import { QueryClient } from "@tanstack/vue-query"

import { ApiError } from "./api/errors"

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 15_000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error instanceof ApiError && [401, 403, 404].includes(error.status)) return false
        return failureCount < 1
      },
    },
    mutations: { retry: false },
  },
})
