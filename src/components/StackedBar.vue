<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const option = computed(() => ({
  grid: { left: 10, right: 10, top: 6, bottom: 22 },
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.date.slice(5)),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569', fontSize: 8, fontFamily: 'Consolas,monospace', interval: 4 },
  },
  yAxis: {
    type: 'value',
    show: false,
    splitLine: { lineStyle: { color: 'rgba(148,163,184,0.06)' } },
  },
  series: [
    {
      name: '缓存命中',
      type: 'bar',
      stack: 'total',
      data: props.data.map((d) => ({
        value: d.cached,
        itemStyle: { color: '#22C55E' },
      })),
      barWidth: '70%',
    },
    {
      name: '未命中缓存',
      type: 'bar',
      stack: 'total',
      data: props.data.map((d) => ({
        value: d.uncached,
        itemStyle: { color: '#3B82F6' },
      })),
      barWidth: '70%',
    },
    {
      name: '输出',
      type: 'bar',
      stack: 'total',
      data: props.data.map((d) => ({
        value: d.output,
        itemStyle: { color: '#8B5CF6' },
      })),
      barWidth: '70%',
    },
  ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(15,23,42,0.95)',
    borderColor: 'rgba(148,163,184,0.12)',
    textStyle: { color: '#E2E8F0', fontSize: 10, fontFamily: 'Consolas,monospace' },
    formatter: (params) => {
      const day = props.data[params[0].dataIndex]
      const lines = params.map((p) => `${p.marker} ${p.seriesName}: ${(p.value || 0).toLocaleString()}`)
      return `<b>${day?.date || ''}</b><br/>${lines.join('<br/>')}<br/><b>总计: ${(day?.cached + day?.uncached + day?.output || 0).toLocaleString()}</b>`
    },
  },
}))
</script>

<template>
  <VChart :option="option" autoresize class="chart" />
</template>

<style scoped>
.chart { width: 100%; height: 100%; min-height: 120px; }
</style>
