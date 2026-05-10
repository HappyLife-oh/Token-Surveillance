<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  trend: { type: Array, default: () => [] },
})

const hasData = computed(() => props.trend.some((d) => d.balance !== null))

const option = computed(() => ({
  grid: { left: 10, right: 10, top: 20, bottom: 22 },
  xAxis: {
    type: 'category',
    data: props.trend.map((d) => d.date.slice(5)),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569', fontSize: 9, fontFamily: 'Consolas,monospace' },
  },
  yAxis: {
    type: 'value',
    show: false,
    splitLine: { lineStyle: { color: 'rgba(148,163,184,0.06)' } },
  },
  series: hasData.value
    ? [
        {
          type: 'bar',
          data: props.trend.map((d) => ({
            value: d.balance,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#3B82F6' },
                  { offset: 1, color: 'rgba(59,130,246,0.15)' },
                ],
              },
              borderRadius: [4, 4, 0, 0],
            },
          })),
          barWidth: '60%',
        },
        {
          type: 'line',
          data: props.trend.map((d) => d.balance),
          smooth: true,
          showSymbol: false,
          lineStyle: { color: '#60a5fa', width: 1.5 },
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(96,165,250,0.15)' },
                { offset: 1, color: 'rgba(96,165,250,0)' },
              ],
            },
          },
        },
      ]
    : [
        {
          type: 'bar',
          data: [],
          barWidth: '60%',
        },
      ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(15,23,42,0.9)',
    borderColor: 'rgba(148,163,184,0.12)',
    textStyle: { color: '#E2E8F0', fontSize: 11, fontFamily: 'Consolas,monospace' },
    formatter: (params) => {
      const p = params[0]
      return `<b>${p.axisValue}</b><br/>Balance: ¥${(p.value || 0).toFixed(2)}`
    },
  },
}))
</script>

<template>
  <div class="wrap">
    <VChart :option="option" autoresize class="chart" />
  </div>
</template>

<style scoped>
.wrap { flex: 1; min-height: 0; width: 100%; }
.chart { width: 100%; height: 100%; min-height: 220px; }
</style>
