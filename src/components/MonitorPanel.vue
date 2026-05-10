<script setup>
import ModelComparison from './ModelComparison.vue'
import AreaChart from './AreaChart.vue'

defineProps({
  modelBreakdown: { type: Array, default: () => [] },
  dailyRequests: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="panel">
    <div class="panel-title drag-handle">
      <div class="title-dot green" />
      <span>模型对比 · 调用频率</span>
    </div>

    <ModelComparison :breakdown="modelBreakdown" />

    <!-- Request frequency area chart -->
    <div class="chart-section">
      <div class="section-label">请求频率 <span class="hint">5月1日 - 5月31日</span></div>
      <div class="chart-container">
        <AreaChart :data="dailyRequests" />
      </div>
    </div>

    <div class="status">
      <span class="st ok">DeepSeek API · Connected</span>
    </div>
  </div>
</template>

<style scoped>
.panel { background: rgba(15,23,42,0.55); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(148,163,184,0.08); border-radius: 16px; padding: 18px 20px; width: 240px; height: 440px; display: flex; flex-direction: column; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.panel-title { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; font-size: 13px; font-weight: 600; color: #e2e8f0; }
.title-dot { width: 6px; height: 6px; border-radius: 50%; }
.title-dot.green { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }
.chart-section { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.section-label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.hint { color: #475569; font-size: 8px; text-transform: none; letter-spacing: 0; }
.chart-container { flex: 1; min-height: 0; width: 100%; }
.status { margin-top: 6px; }
.st { font-size: 9px; }
.st.ok { color: #475569; }
</style>
