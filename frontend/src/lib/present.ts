import { reactive } from "vue"

export function presentQuery<T>(query: {
  data: { value: T }
  error: { value: unknown }
  isPending: { value: boolean }
  isError: { value: boolean }
  refetch: () => Promise<unknown>
}) {
  return reactive({
    get data(): T {
      return query.data.value
    },
    get error(): unknown {
      return query.error.value
    },
    get isPending(): boolean {
      return query.isPending.value
    },
    get isError(): boolean {
      return query.isError.value
    },
    refetch: () => query.refetch(),
  })
}

export function presentMutation<TArgs extends unknown[], TResult>(mutation: {
  isPending: { value: boolean }
  mutateAsync: (...args: TArgs) => Promise<TResult>
}) {
  return reactive({
    get isPending(): boolean {
      return mutation.isPending.value
    },
    mutateAsync: (...args: TArgs) => mutation.mutateAsync(...args),
  })
}
