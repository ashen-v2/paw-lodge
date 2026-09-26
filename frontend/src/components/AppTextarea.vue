<script setup lang="ts">
import { inputClass } from "../lib/ui"

const model = defineModel<string>({ required: true })

defineProps<{
  id: string
  invalid?: boolean
  rows?: number
}>()
</script>

<template>
  <textarea
    :id="id"
    v-model="model"
    :rows="rows ?? 3"
    :class="inputClass(invalid)"
    :aria-invalid="invalid || undefined"
    :aria-describedby="invalid ? `${id}-error` : undefined"
  />
</template>
