import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query"
import { computed } from "vue"

import { fetchMe, login, registerPractice } from "../api/endpoints"
import type { LoginBody, RegisterBody } from "../api/types"
import { setToken, token } from "../auth/session"

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    enabled: computed(() => Boolean(token.value)),
    retry: false,
  })
}

export function useLogin() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async (body: LoginBody) => {
      const result = await login(body)
      setToken(result.access_token)
      return result
    },
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["me"] })
    },
  })
}

export function useRegister() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async (body: RegisterBody) => {
      await registerPractice(body)
      const result = await login({ email: body.email, password: body.password })
      setToken(result.access_token)
      return result
    },
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["me"] })
    },
  })
}
