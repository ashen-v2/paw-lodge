import { ref } from "vue"

const STORAGE_KEY = "pawlodge.token"

export const token = ref<string | null>(localStorage.getItem(STORAGE_KEY))

export function getToken(): string | null {
  return token.value
}

export function setToken(value: string): void {
  token.value = value
  localStorage.setItem(STORAGE_KEY, value)
}

export function clearToken(): void {
  token.value = null
  localStorage.removeItem(STORAGE_KEY)
}
