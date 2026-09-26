<script setup lang="ts">
import {
  CategoryScale,
  Chart,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js"
import { nextTick, onBeforeUnmount, ref, watch } from "vue"

import { formatDate } from "../lib/dates"
import { formatMoney } from "../lib/money"

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip)

const props = defineProps<{ points: { date: string; revenue: number }[] }>()

const canvas = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

async function render() {
  await nextTick()
  if (!canvas.value || props.points.length === 0) {
    chart?.destroy()
    chart = null
    return
  }
  const labels = props.points.map((point) => formatDate(point.date))
  const values = props.points.map((point) => Number(point.revenue))
  chart?.destroy()
  chart = new Chart(canvas.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          data: values,
          borderColor: "#1f7a5c",
          backgroundColor: "rgba(31, 122, 92, 0.14)",
          fill: true,
          tension: 0.25,
          pointRadius: 3,
          pointBackgroundColor: "#1f7a5c",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (item) => formatMoney(item.parsed.y),
          },
        },
      },
      scales: {
        x: {
          ticks: { maxRotation: 0, autoSkip: true, color: "#5c675f", font: { family: "IBM Plex Sans" } },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: "#5c675f",
            font: { family: "IBM Plex Sans" },
            callback: (value) => formatMoney(Number(value)),
          },
        },
      },
    },
  })
}

watch(
  () => props.points.map((point) => `${point.date}:${point.revenue}`).join("|"),
  () => {
    void render()
  },
  { immediate: true },
)

onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div>
    <p v-if="points.length === 0" class="text-sm text-muted">No payments in this range.</p>
    <template v-else>
      <div class="h-56">
        <canvas ref="canvas" role="img" aria-label="Revenue chart. Each day is also listed below." />
      </div>
      <ul class="mt-4 max-h-64 divide-y divide-line overflow-y-auto text-sm">
        <li v-for="point in points" :key="point.date" class="flex items-center justify-between gap-3 py-2">
          <span>{{ formatDate(point.date) }}</span>
          <span class="tabular-nums">{{ formatMoney(point.revenue) }}</span>
        </li>
      </ul>
    </template>
  </div>
</template>
