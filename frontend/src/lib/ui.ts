export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger"

export function buttonClass(variant: ButtonVariant = "primary", block = false): string {
  const base =
    "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60"
  const variants: Record<ButtonVariant, string> = {
    primary: "bg-leaf text-white hover:bg-leaf-dark",
    secondary: "border border-line bg-card text-ink hover:bg-paper",
    ghost: "text-ink hover:bg-black/5",
    danger: "bg-danger text-white hover:brightness-95",
  }
  return [base, variants[variant], block ? "w-full" : ""].filter(Boolean).join(" ")
}

export function inputClass(invalid = false): string {
  return [
    "min-h-11 w-full rounded-xl border bg-card px-3 text-base text-ink placeholder:text-muted/70",
    invalid ? "border-danger" : "border-line",
  ].join(" ")
}
