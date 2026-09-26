<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"

import { confirmState, settleConfirm } from "../lib/confirm"
import { buttonClass } from "../lib/ui"
import AppButton from "./AppButton.vue"

const cancelRef = ref<HTMLButtonElement | null>(null)

watch(
  () => confirmState.current,
  async (current) => {
    if (!current) return
    await nextTick()
    cancelRef.value?.focus()
  },
)

function onKey(event: KeyboardEvent) {
  if (event.key === "Escape" && confirmState.current) settleConfirm(false)
}

onMounted(() => window.addEventListener("keydown", onKey))
onBeforeUnmount(() => window.removeEventListener("keydown", onKey))
</script>

<template>
  <div
    v-if="confirmState.current"
    class="fixed inset-0 z-[70] flex items-end justify-center p-4 sm:items-center"
  >
    <div class="absolute inset-0 bg-ink/40" />
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
      aria-describedby="confirm-message"
      class="relative w-full max-w-md rounded-2xl border border-line bg-card p-5 shadow-lg"
    >
      <h2 id="confirm-title" class="font-serif text-2xl text-ink">{{ confirmState.current.title }}</h2>
      <p id="confirm-message" class="mt-2 text-sm text-muted">{{ confirmState.current.message }}</p>
      <div class="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <button
          ref="cancelRef"
          type="button"
          :class="buttonClass('secondary')"
          @click="settleConfirm(false)"
        >
          Cancel
        </button>
        <AppButton
          :variant="confirmState.current.danger ? 'danger' : 'primary'"
          @click="settleConfirm(true)"
        >
          {{ confirmState.current.confirmLabel }}
        </AppButton>
      </div>
    </div>
  </div>
</template>
