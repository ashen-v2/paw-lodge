import { reactive } from "vue"

type ConfirmRequest = {
  title: string
  message: string
  confirmLabel: string
  danger: boolean
  resolve: (value: boolean) => void
}

export const confirmState = reactive<{ current: ConfirmRequest | null }>({ current: null })

export function askConfirm(options: {
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
}): Promise<boolean> {
  return new Promise((resolve) => {
    confirmState.current = {
      title: options.title,
      message: options.message,
      confirmLabel: options.confirmLabel ?? "Confirm",
      danger: options.danger ?? true,
      resolve,
    }
  })
}

export function settleConfirm(value: boolean): void {
  const current = confirmState.current
  if (!current) return
  confirmState.current = null
  current.resolve(value)
}
