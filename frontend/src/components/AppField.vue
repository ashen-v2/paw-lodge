<script setup lang="ts">
defineProps<{
  label: string
  fieldId: string
  error?: string
  hint?: string
}>()
</script>

<template>
  <div class="grid gap-1.5">
    <label :for="fieldId" class="text-sm font-medium text-ink">{{ label }}</label>
    <slot />
    <p v-if="error" :id="`${fieldId}-error`" class="text-sm text-danger" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="`${fieldId}-hint`" class="text-sm text-muted">{{ hint }}</p>
  </div>
</template>
