export function visitPayStatus(
  outstanding: number,
  hasPayment: boolean,
): { tone: "ok" | "warn" | "danger"; label: string } {
  if (hasPayment && outstanding <= 0.009) return { tone: "ok", label: "Paid" }
  if (hasPayment) return { tone: "warn", label: "Part paid" }
  return { tone: "danger", label: "Unpaid" }
}

export function methodLabel(method: string): string {
  if (method === "cash") return "Cash"
  if (method === "other") return "Other"
  return method
}
