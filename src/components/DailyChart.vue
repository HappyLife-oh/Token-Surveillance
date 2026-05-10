<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  summaries: { type: Array, default: () => [] },
})

const chartData = computed(() => {
  if (props.summaries.length) return props.summaries
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push({ date: d.toISOString().slice(0, 10), total_tokens: 0 })
  }
  return days
})

const option = computed(() => ({
  grid: { left: 6, right: 6, top: 28, bottom: 22 },
  xAxis: {
    type: 'category',
    data: chartData.value.map((s) => s.date.slice(5)),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569', fontSize: 9, fontFamily: 'Consolas,monospace' },
  },
  yAxis: {
    type: 'value',
    show: false,
    splitLine: { lineStyle: { color: 'rgba(148,163,184,0.06)' } },
    max: (val) => Math.ceil(val.max * 1.2),
  },
  series: [
    {
      type: 'bar',
      data: chartData.value.map((s) => {
        const max = Math.max(...chartData.value.map((x) => x.total_tokens), 1)
        return {
          value: s.total_tokens,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: s.total_tokens >= max ? '#3B82F6' : '#2563EB' },
                { offset: 1, color: s.total_tokens >= max ? 'rgba(59,130,246,0.3)' : 'rgba(37,99,235,0.15)' },
              ],
            },
            borderRadius: [4, 4, 0, 0],
          },
          label: {
            show: s.total_tokens > 0,
            position: 'top',
            color: '#94A3B8',
            fontSize: 9,
            fontFamily: 'Consolas,monospace',
            formatter: (p) => {
              const v = p.value
              if (v >= 1e6) return (v / 1e6).toFixed(2) + 'M'
              if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K'
              return v.toString()
            },
          },
        }
      }),
      barWidth: '70%',
    },
  ],
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15,23,42,0.9)',
    borderColor: 'rgba(148,163,184,0.12)',
    textStyle: { color: '#E2E8F0', fontSize: 11, fontFamily: 'Consolas,monospace' },
    formatter: ({ name, value }) =>
      `<b>${name}</b><br/>Tokens: ${(value || 0).toLocaleString()}`,
  },
}))
</script>

<template>
  <div class="chart-wrap">
    <VChart :option="option" autoresize class="chart" />
  </div>
</template>

<style scoped>
.chart-wrap {
  flex: 1;
  min-height: 0;
  width: 100%;
}
.chart {
  width: 100%;
  height: 100%;
  min-height: 220px;
}
</style>
