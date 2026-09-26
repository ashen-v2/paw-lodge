<script setup lang="ts">
defineProps<{ items: { label: string; to?: string }[] }>()
</script>

<template>
  <nav aria-label="Breadcrumb" class="mb-3 text-sm text-muted">
    <ol class="flex flex-wrap items-center gap-x-1 gap-y-1">
      <li v-for="(item, index) in items" :key="`${item.label}-${index}`" class="flex items-center gap-1">
        <RouterLink v-if="item.to" :to="item.to" class="underline-offset-2 hover:underline">{{ item.label }}</RouterLink>
        <span v-else class="text-ink" aria-current="page">{{ item.label }}</span>
        <span v-if="index < items.length - 1" aria-hidden="true">/</span>
      </li>
    </ol>
  </nav>
</template>
