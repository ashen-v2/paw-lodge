<script setup lang="ts">
import { inputClass } from "../lib/ui"

const model = defineModel<string>({ required: true })

defineProps<{
  id: string
  invalid?: boolean
}>()
</script>

<template>
  <select
    :id="id"
    v-model="model"
    :class="inputClass(invalid)"
    :aria-invalid="invalid || undefined"
    :aria-describedby="invalid ? `${id}-error` : undefined"
  >
    <slot />
  </select>
</template>
