import createClient from "openapi-fetch"

import { getToken } from "../auth/session"
import type { paths } from "./generated/schema"
import { toApiError } from "./errors"

const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

export const api = createClient<paths>({ baseUrl })

let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

api.use({
  onRequest({ request }) {
    const current = getToken()
    if (current) request.headers.set("Authorization", `Bearer ${current}`)
    return request
  },
})

const PUBLIC_AUTH = ["/api/v1/auth/login", "/api/v1/auth/register"]

type ApiResult<T> = {
  data?: T
  error?: unknown
  response: Response
}

export async function unwrap<T>(pending: Promise<ApiResult<T>>): Promise<T> {
  const result = await pending
  if (result.response.ok) return result.data as T
  const path = new URL(result.response.url).pathname
  if (result.response.status === 401 && !PUBLIC_AUTH.includes(path)) onUnauthorized?.()
  throw toApiError(result.response.status, result.error)
}

export async function unwrapEmpty(pending: Promise<ApiResult<never>>): Promise<void> {
  const result = await pending
  if (result.response.ok) return
  const path = new URL(result.response.url).pathname
  if (result.response.status === 401 && !PUBLIC_AUTH.includes(path)) onUnauthorized?.()
  throw toApiError(result.response.status, result.error)
}
