<script setup lang="ts">
import { errorMessage } from "../api/errors"
import AppButton from "./AppButton.vue"

defineProps<{ error: unknown }>()
const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="rounded-2xl border border-line bg-card px-4 py-5" role="alert">
    <p class="text-sm text-ink">{{ errorMessage(error) }}</p>
    <AppButton class="mt-3" variant="secondary" @click="emit('retry')">Try again</AppButton>
  </div>
</template>
