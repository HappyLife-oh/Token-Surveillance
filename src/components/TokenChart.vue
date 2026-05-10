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

const maxVal = computed(() => {
  return Math.max(...chartData.value.map((s) => s.total_tokens), 1)
})

const option = computed(() => ({
  grid: { left: 0, right: 0, top: 4, bottom: 16, containLabel: true },
  xAxis: {
    type: 'category',
    data: chartData.value.map((s) => s.date.slice(5)),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      color: '#64748B',
      fontSize: 8,
      fontFamily: 'monospace',
    },
  },
  yAxis: {
    type: 'value',
    show: false,
    splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
  },
  series: [
    {
      type: 'bar',
      data: chartData.value.map((s) => ({
        value: s.total_tokens,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: s.total_tokens >= maxVal.value ? '#D97706' : '#059669' },
              { offset: 1, color: s.total_tokens >= maxVal.value ? '#D9770620' : '#05966920' },
            ],
          },
          borderRadius: [3, 3, 0, 0],
        },
      })),
      barWidth: '70%',
    },
  ],
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0E1223',
    borderColor: '#1E293B',
    textStyle: { color: '#E2E8F0', fontSize: 10, fontFamily: 'monospace' },
    formatter: ({ name, value }) =>
      `${name}<br/>Tokens: ${(value || 0).toLocaleString()}`,
  },
}))
</script>

<template>
  <div class="wrapper">
    <div class="title">7-DAY TOKEN USAGE</div>
    <VChart :option="option" autoresize class="chart" />
  </div>
</template>

<style scoped>
.wrapper {
  background: #0e1223;
  border-radius: 6px;
  padding: 10px 8px;
  margin-bottom: 8px;
}
.title {
  color: #64748b;
  font-size: 9px;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.chart {
  height: 100px;
  width: 100%;
}
</style>
