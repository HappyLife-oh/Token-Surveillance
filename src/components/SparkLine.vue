<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const pathD = computed(() => {
  if (!props.data.length) return ''
  const w = 280
  const h = 36
  const max = Math.max(...props.data, 1)
  const pad = 2
  const availH = h - pad * 2
  const availW = w - pad * 2
  const stepX = availW / (props.data.length - 1)
  return props.data
    .map((v, i) => {
      const x = pad + i * stepX
      const y = pad + availH - (v / max) * availH
      return `${i === 0 ? 'M' : 'L'}${x},${y}`
    })
    .join(' ')
})

const areaD = computed(() => {
  if (!props.data.length) return ''
  const w = 280
  const h = 36
  const max = Math.max(...props.data, 1)
  const pad = 2
  const availH = h - pad * 2
  const availW = w - pad * 2
  const stepX = availW / (props.data.length - 1)
  const pts = props.data.map((v, i) => {
    const x = pad + i * stepX
    const y = pad + availH - (v / max) * availH
    return `${x},${y}`
  })
  const last = pts[pts.length - 1].split(',')
  const first = pts[0].split(',')
  return `M${pts.join('L')}L${last[0]},${h - pad}L${first[0]},${h - pad}Z`
})
</script>

<template>
  <div class="sparkline">
    <svg width="100%" height="36" viewBox="0 0 280 36">
      <defs>
        <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(59,130,246,0.25)" />
          <stop offset="100%" stop-color="rgba(59,130,246,0)" />
        </linearGradient>
      </defs>
      <path :d="areaD" fill="url(#sparkFill)" />
      <path :d="pathD" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round" />
    </svg>
  </div>
</template>

<style scoped>
.sparkline {
  width: 100%;
}
</style>
