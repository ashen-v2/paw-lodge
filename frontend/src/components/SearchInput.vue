<script setup lang="ts">
import { inputClass } from "../lib/ui"

const model = defineModel<string>({ required: true })

defineProps<{
  id: string
  label: string
}>()
</script>

<template>
  <div class="grid gap-1.5">
    <label :for="id" class="text-sm font-medium text-ink">{{ label }}</label>
    <input :id="id" v-model="model" type="search" :class="inputClass(false)" autocomplete="off" />
  </div>
</template>
