<script setup lang="ts">
defineProps<{ className?: string }>()
</script>

<template>
  <div class="animate-pulse rounded-2xl bg-line/80" :class="className" aria-hidden="true" />
</template>
