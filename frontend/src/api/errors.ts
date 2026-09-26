type ValidationItem = {
  loc?: Array<string | number>
  msg?: string
}

export class ApiError extends Error {
  status: number
  fields: Record<string, string>

  constructor(status: number, message: string, fields: Record<string, string> = {}) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.fields = fields
  }
}

function cleanMessage(message: string): string {
  return message.replace(/^Value error,\s*/i, "").replace(/^Assertion failed,\s*/i, "")
}

function fieldsFrom(detail: unknown): Record<string, string> {
  if (!Array.isArray(detail)) return {}
  const fields: Record<string, string> = {}
  for (const item of detail as ValidationItem[]) {
    const loc = item.loc ?? []
    const key = String(loc[loc.length - 1] ?? "")
    if (!key || key === "body" || !item.msg) continue
    fields[key] = cleanMessage(item.msg)
  }
  return fields
}

function messageFrom(status: number, body: unknown): string {
  const detail =
    body && typeof body === "object" && "detail" in body
      ? (body as { detail: unknown }).detail
      : undefined
  if (typeof detail === "string" && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : ""))
      .map(cleanMessage)
      .filter(Boolean)
    if (messages.length) return messages.join(" ")
    return "Check the form and try again."
  }
  if (status === 401) return "Email or password is incorrect."
  if (status === 403) return "You do not have permission to do that."
  if (status === 404) return "That record was not found."
  if (status === 409) return "That conflicts with an existing record."
  if (status === 400) return "That action is not allowed."
  return "Something went wrong. Please try again."
}

export function toApiError(status: number, body: unknown): ApiError {
  const detail =
    body && typeof body === "object" && "detail" in body
      ? (body as { detail: unknown }).detail
      : undefined
  return new ApiError(status, messageFrom(status, body), fieldsFrom(detail))
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof TypeError) return "Cannot reach the clinic server. Check that the API is running."
  return "Something went wrong. Please try again."
}
