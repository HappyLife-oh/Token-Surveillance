<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const option = computed(() => ({
  grid: { left: 10, right: 10, top: 8, bottom: 22 },
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
      type: 'line',
      data: props.data.map((d) => d.total),
      smooth: true,
      showSymbol: false,
      lineStyle: { color: '#3B82F6', width: 2 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(59,130,246,0.3)' },
            { offset: 1, color: 'rgba(59,130,246,0)' },
          ],
        },
      },
    },
  ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(15,23,42,0.95)',
    borderColor: 'rgba(148,163,184,0.12)',
    textStyle: { color: '#E2E8F0', fontSize: 10, fontFamily: 'Consolas,monospace' },
    formatter: (params) => {
      const p = params[0]
      const day = props.data[p.dataIndex]
      return `<b>${day?.date || p.axisValue}</b><br/>调用次数: ${p.value}<br/>V4 Flash: ${day?.flash || 0} · V4 Pro: ${day?.pro || 0}`
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
