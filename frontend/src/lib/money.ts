/** The practice API has no currency field. Rs. is the display currency for this clinic app. */
const CURRENCY_LABEL = "Rs."

export function formatMoney(amount: number | string | null | undefined): string {
  const value = typeof amount === "number" ? amount : Number(amount ?? 0)
  const safe = Number.isFinite(value) ? value : 0
  const formatted = safe.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${CURRENCY_LABEL} ${formatted}`
}

export function lineAmount(quantity: number, unitPrice: number): number {
  return Math.round(quantity * unitPrice * 100) / 100
}
