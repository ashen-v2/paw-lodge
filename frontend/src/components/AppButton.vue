<script setup lang="ts">
import { buttonClass, type ButtonVariant } from "../lib/ui"

withDefaults(
  defineProps<{
    type?: "button" | "submit"
    variant?: ButtonVariant
    disabled?: boolean
    block?: boolean
  }>(),
  { type: "button", variant: "primary", disabled: false, block: false },
)
</script>

<template>
  <button :type="type" :disabled="disabled" :class="buttonClass(variant, block)">
    <slot />
  </button>
</template>
