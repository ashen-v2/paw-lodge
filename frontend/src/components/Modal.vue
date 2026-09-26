<script setup lang="ts">
import { onBeforeUnmount, onMounted, watch } from "vue"

const props = defineProps<{
  open: boolean
  title: string
}>()

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
  <div v-if="open" class="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
    <button
      type="button"
      class="absolute inset-0 bg-ink/40"
      aria-label="Close dialog"
      @click="emit('close')"
    />
    <div
      role="dialog"
      aria-modal="true"
      :aria-label="title"
      class="relative max-h-[92dvh] w-full overflow-y-auto rounded-t-2xl border border-line bg-card p-5 shadow-lg sm:max-w-lg sm:rounded-2xl"
    >
      <div class="mb-4 flex items-start justify-between gap-3">
        <h2 class="font-serif text-2xl text-ink">{{ title }}</h2>
        <button type="button" class="min-h-11 min-w-11 rounded-xl text-sm text-muted" @click="emit('close')">
          Close
        </button>
      </div>
      <slot />
    </div>
  </div>
</template>
