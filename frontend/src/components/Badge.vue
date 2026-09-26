<script setup lang="ts">
withDefaults(defineProps<{ tone?: "neutral" | "ok" | "warn" | "danger" }>(), { tone: "neutral" })

const tones = {
  neutral: "bg-paper text-ink",
  ok: "bg-ok-bg text-ok",
  warn: "bg-warn-bg text-warn",
  danger: "bg-danger-bg text-danger",
}
</script>

<template>
  <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium" :class="tones[tone]">
    <slot />
  </span>
</template>
