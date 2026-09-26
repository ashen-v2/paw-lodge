export type DateRange = { from: string; to: string }

export function utcToday(): string {
  return new Date().toISOString().slice(0, 10)
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—"
  const [year, month, day] = value.slice(0, 10).split("-").map(Number)
  if (!year || !month || !day) return value
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, day)))
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

export function ageLabel(dateOfBirth: string | null | undefined): string | null {
  if (!dateOfBirth) return null
  const [year, month, day] = dateOfBirth.slice(0, 10).split("-").map(Number)
  if (!year || !month || !day) return null
  const today = utcToday().split("-").map(Number)
  const nowYear = today[0] ?? 0
  const nowMonth = today[1] ?? 1
  const nowDay = today[2] ?? 1
  let months = (nowYear - year) * 12 + (nowMonth - month)
  if (nowDay < day) months -= 1
  if (months < 0) return null
  if (months < 12) return months === 1 ? "1 month" : `${months} months`
  const years = Math.floor(months / 12)
  const remainder = months % 12
  if (remainder === 0) return years === 1 ? "1 year" : `${years} years`
  return `${years} yr ${remainder} mo`
}

export function thisMonthRange(today = utcToday()): DateRange {
  return { from: `${today.slice(0, 8)}01`, to: today }
}

export function lastMonthRange(today = utcToday()): DateRange {
  const [year, month] = today.split("-").map(Number)
  const start = new Date(Date.UTC(year ?? 2026, (month ?? 1) - 2, 1))
  const end = new Date(Date.UTC(year ?? 2026, (month ?? 1) - 1, 0))
  return {
    from: start.toISOString().slice(0, 10),
    to: end.toISOString().slice(0, 10),
  }
}

export function lastDaysRange(days: number, today = utcToday()): DateRange {
  const [year, month, day] = today.split("-").map(Number)
  const start = new Date(Date.UTC(year ?? 2026, (month ?? 1) - 1, (day ?? 1) - (days - 1)))
  return { from: start.toISOString().slice(0, 10), to: today }
}

export function isBeforeDay(value: string | null | undefined, day = utcToday()): boolean {
  if (!value) return false
  return value.slice(0, 10) < day
}

export function greetingFor(name: string): string {
  const hour = new Date().getHours()
  const part = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening"
  const titles = new Set(["dr", "dr.", "mr", "mr.", "mrs", "mrs.", "ms", "ms."])
  const parts = name.trim().split(/\s+/).filter(Boolean)
  const first = parts.find((token) => !titles.has(token.toLowerCase())) ?? parts[0] ?? name
  return `${part}, ${first}`
}

export function roleLabel(role: string): string {
  if (role === "owner") return "Owner"
  if (role === "staff") return "Staff"
  return role
}
