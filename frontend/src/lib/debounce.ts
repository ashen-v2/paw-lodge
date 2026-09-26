import { ref, watch, type Ref } from "vue"

export function useDebounced(source: Ref<string>, wait = 300): Ref<string> {
  const debounced = ref(source.value)
  let timer = 0
  watch(source, (value) => {
    window.clearTimeout(timer)
    timer = window.setTimeout(() => {
      debounced.value = value
    }, wait)
  })
  return debounced
}
