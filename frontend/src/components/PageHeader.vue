<script setup lang="ts">
defineProps<{
  title: string
  eyebrow?: string
  description?: string
}>()
</script>

<template>
  <header class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
    <div class="min-w-0">
      <p v-if="eyebrow" class="text-xs font-medium uppercase tracking-[0.14em] text-muted">{{ eyebrow }}</p>
      <h1 class="mt-1 break-words font-serif text-3xl text-ink sm:text-4xl">{{ title }}</h1>
      <p v-if="description" class="mt-2 max-w-2xl text-sm text-muted">{{ description }}</p>
    </div>
    <div class="flex flex-wrap gap-2">
      <slot name="actions" />
    </div>
  </header>
</template>
