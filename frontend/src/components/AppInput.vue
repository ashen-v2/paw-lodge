<script setup lang="ts">
import { inputClass } from "../lib/ui"

const model = defineModel<string | number>({ required: true })

function onInput(event: Event) {
  const target = event.target
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
    model.value = target.value
  }
}

withDefaults(
  defineProps<{
    id: string
    type?: string
    invalid?: boolean
    autocomplete?: string
    inputmode?: "text" | "email" | "tel" | "numeric" | "decimal" | "search"
    maxlength?: number | string
    min?: string
    max?: string
    step?: string
    placeholder?: string
    ariaLabel?: string
  }>(),
  { type: "text", invalid: false },
)
</script>

<template>
  <input
    :id="id"
    :value="model"
    :type="type"
    @input="onInput"
    :class="inputClass(invalid)"
    :autocomplete="autocomplete"
    :inputmode="inputmode"
    :maxlength="maxlength"
    :min="min"
    :max="max"
    :step="step"
    :placeholder="placeholder"
    :aria-label="ariaLabel"
    :aria-invalid="invalid || undefined"
    :aria-describedby="invalid ? `${id}-error` : undefined"
  />
</template>
