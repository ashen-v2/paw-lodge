<script setup lang="ts">
defineProps<{
  label: string
  value: string
  detail?: string
}>()
</script>

<template>
  <article class="rounded-2xl border border-line bg-card px-4 py-4">
    <p class="text-sm text-muted">{{ label }}</p>
    <p class="mt-2 font-serif text-3xl tabular-nums text-ink">{{ value }}</p>
    <p v-if="detail" class="mt-1 text-sm text-muted">{{ detail }}</p>
  </article>
</template>
