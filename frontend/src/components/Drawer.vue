<script setup lang="ts">
import { onBeforeUnmount, onMounted, watch } from "vue"

const props = defineProps<{ open: boolean; title: string }>()
const emit = defineEmits<{ close: [] }>()

function onKey(event: KeyboardEvent) {
  if (event.key === "Escape" && props.open) emit("close")
}

onMounted(() => window.addEventListener("keydown", onKey))
onBeforeUnmount(() => window.removeEventListener("keydown", onKey))

watch(
  () => props.open,
  (open) => {
    document.body.style.overflow = open ? "hidden" : ""
  },
)
onBeforeUnmount(() => {
  document.body.style.overflow = ""
})
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-40 lg:hidden">
    <button type="button" class="absolute inset-0 bg-ink/40" aria-label="Close menu" @click="emit('close')" />
    <div
      role="dialog"
      aria-modal="true"
      :aria-label="title"
      class="absolute inset-y-0 right-0 flex w-[min(100%,20rem)] flex-col bg-card shadow-lg"
    >
      <div class="flex items-center justify-between border-b border-line px-4 py-3">
        <h2 class="font-serif text-xl">{{ title }}</h2>
        <button type="button" class="min-h-11 px-3 text-sm" @click="emit('close')">Close</button>
      </div>
      <div class="flex-1 overflow-y-auto p-3">
        <slot />
      </div>
    </div>
  </div>
</template>
