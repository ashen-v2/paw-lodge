<script setup lang="ts">
defineProps<{ title: string; body: string }>()
</script>

<template>
  <div class="rounded-2xl border border-dashed border-line bg-card px-5 py-10 text-center">
    <h2 class="font-serif text-2xl text-ink">{{ title }}</h2>
    <p class="mx-auto mt-2 max-w-md text-sm text-muted">{{ body }}</p>
    <div class="mt-5 flex justify-center">
      <slot />
    </div>
  </div>
</template>
