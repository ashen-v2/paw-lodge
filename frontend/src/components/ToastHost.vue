<script setup lang="ts">
import { dismissToast, toasts, type ToastKind } from "../lib/toast"

function kindLabel(kind: ToastKind): string {
  if (kind === "success") return "Success"
  if (kind === "warning") return "Note"
  return "Problem"
}
</script>

<template>
  <div class="pointer-events-none fixed inset-x-0 top-16 z-[60] flex flex-col items-center gap-2 px-4 lg:top-4 lg:items-end">
    <article
      v-for="item in toasts"
      :key="item.id"
      class="pointer-events-auto w-full max-w-sm rounded-xl border px-4 py-3 text-sm shadow-sm"
      :class="
        item.kind === 'error'
          ? 'border-danger/30 bg-danger-bg text-danger'
          : item.kind === 'warning'
            ? 'border-warn/30 bg-warn-bg text-warn'
            : 'border-line bg-card text-ink'
      "
      :role="item.kind === 'error' ? 'alert' : 'status'"
    >
      <div class="flex items-start justify-between gap-3">
        <p>
          <span class="font-semibold">{{ kindLabel(item.kind) }}: </span>{{ item.text }}
        </p>
        <button type="button" class="min-h-11 shrink-0 px-1 text-xs font-medium" @click="dismissToast(item.id)">
          Dismiss
        </button>
      </div>
    </article>
  </div>
</template>
