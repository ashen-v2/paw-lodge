import { ref } from "vue"

export type ToastKind = "success" | "error" | "warning"

export type ToastItem = {
  id: number
  kind: ToastKind
  text: string
}

export const toasts = ref<ToastItem[]>([])

let nextId = 1

function push(kind: ToastKind, text: string): void {
  const id = nextId
  nextId += 1
  toasts.value = [...toasts.value, { id, kind, text }]
  window.setTimeout(() => {
    toasts.value = toasts.value.filter((item) => item.id !== id)
  }, 4500)
}

export const toast = {
  success: (text: string) => push("success", text),
  error: (text: string) => push("error", text),
  warning: (text: string) => push("warning", text),
}

export function dismissToast(id: number): void {
  toasts.value = toasts.value.filter((item) => item.id !== id)
}
