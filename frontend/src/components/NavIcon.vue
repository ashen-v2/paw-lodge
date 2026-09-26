<script setup lang="ts">
defineProps<{
  name: "home" | "paw" | "people" | "clipboard" | "tag" | "syringe" | "chart" | "gear"
}>()
</script>

<template>
  <svg viewBox="0 0 24 24" class="size-5 shrink-0" aria-hidden="true">
    <path
      v-if="name === 'home'"
      fill="none"
      stroke="currentColor"
      stroke-width="1.75"
      d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-9.5Z"
    />
    <g v-else-if="name === 'paw'" fill="currentColor">
      <ellipse cx="12" cy="16.2" rx="4" ry="3" />
      <ellipse cx="7.2" cy="10.2" rx="1.55" ry="2" />
      <ellipse cx="11" cy="8.3" rx="1.55" ry="2" />
      <ellipse cx="14.8" cy="8.6" rx="1.55" ry="2" />
      <ellipse cx="17.7" cy="11.2" rx="1.45" ry="1.9" />
    </g>
    <g v-else-if="name === 'people'" fill="none" stroke="currentColor" stroke-width="1.75">
      <circle cx="9" cy="8" r="2.4" />
      <path d="M4.5 18.5c.6-2.6 2.4-4 4.5-4s3.9 1.4 4.5 4" />
      <circle cx="16.5" cy="8.5" r="2" />
      <path d="M15.2 14.6c1.6.3 2.9 1.4 3.5 3.4" />
    </g>
    <g v-else-if="name === 'clipboard'" fill="none" stroke="currentColor" stroke-width="1.75">
      <rect x="6" y="4.5" width="12" height="15.5" rx="2" />
      <path d="M9 4.5h6v2H9zM9 11h6M9 14.5h4" />
    </g>
    <g v-else-if="name === 'tag'" fill="none" stroke="currentColor" stroke-width="1.75">
      <path d="M4 12.5 12.2 4.5H19v6.8l-8 7.7L4 12.5Z" />
      <circle cx="15.2" cy="8.2" r="1" fill="currentColor" stroke="none" />
    </g>
    <g v-else-if="name === 'syringe'" fill="none" stroke="currentColor" stroke-width="1.75">
      <path d="m14.5 4.5 5 5M8 11l5-5 5 5-5 5-5-5Z" />
      <path d="m8 11-4 4 2.5 2.5 4-4M6.5 16.5 4 19" />
    </g>
    <g v-else-if="name === 'chart'" fill="none" stroke="currentColor" stroke-width="1.75">
      <path d="M4 19h16M7 16V10M12 16V6M17 16v-4" />
    </g>
    <g v-else fill="none" stroke="currentColor" stroke-width="1.75">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 4.5v2.2M12 17.3v2.2M4.5 12h2.2M17.3 12h2.2M6.6 6.6l1.6 1.6M15.8 15.8l1.6 1.6M17.4 6.6l-1.6 1.6M8.2 15.8l-1.6 1.6" />
    </g>
  </svg>
</template>
