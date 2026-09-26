export function blankToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

export function moneyInput(value: number | string | null | undefined): string {
  const number = typeof value === "number" ? value : Number(value ?? 0)
  if (!Number.isFinite(number)) return "0.00"
  return number.toFixed(2)
}
