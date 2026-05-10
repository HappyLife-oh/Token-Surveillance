<script setup>
import SparkLine from './SparkLine.vue'

defineProps({
  totalBalance: Number,
  grantedBalance: Number,
  toppedUpBalance: Number,
  isAvailable: Boolean,
  monthlySpending: [Number, null],
  modelBreakdown: Array,
  balanceTrend: Array,
  sparklineData: Array,
  syncTime: String,
  error: String,
})
</script>

<template>
  <div class="panel">
    <div class="panel-title drag-handle">
      <div class="title-dot blue" />
      <span>账户概览</span>
    </div>

    <!-- Balance -->
    <div class="section">
      <div class="label">账户余额</div>
      <div class="balance-row">
        <span class="balance-num">¥{{ (totalBalance || 0).toFixed(2) }}</span>
        <span v-if="isAvailable" class="badge success">● 可用</span>
        <span v-else class="badge error">● 不可用</span>
      </div>
    </div>

    <div class="section">
      <div class="sub-row"><span class="sub-label">赠送金</span><span class="sub-val">¥{{ (grantedBalance || 0).toFixed(2) }}</span></div>
      <div class="sub-row"><span class="sub-label">充值金</span><span class="sub-val topped">¥{{ (toppedUpBalance || 0).toFixed(2) }}</span></div>
    </div>

    <!-- Monthly spending -->
    <div class="section">
      <div class="label">本月消费</div>
      <div class="spend-row">
        <template v-if="monthlySpending !== null">
          <span class="spend-num">¥{{ monthlySpending.toFixed(2) }}</span>
          <span class="sub-label" style="margin-left:6px">(余额变化)</span>
        </template>
        <span v-else class="sub-label">持续追踪中</span>
      </div>
    </div>

    <!-- Balance chart -->
    <div class="section chart-section">
      <div class="label">余额趋势</div>
      <div class="mini-chart-wrap">
        <SparkLine :data="sparklineData" />
      </div>
    </div>

    <!-- Model breakdown summary -->
    <div class="section" style="flex:1">
      <div class="label">模型用量概览</div>
      <div class="model-summary">
        <div v-for="m in modelBreakdown" :key="m.id" class="ms-row">
          <span class="ms-name" :style="{ color: m.color }">{{ m.label }}</span>
          <div class="ms-track">
            <div class="ms-fill" :style="{
              width: Math.min(100, m.count > 0 ? (m.count / Math.max(...modelBreakdown.map(x=>x.count), 1)) * 100 : 0) + '%',
              background: m.color,
            }"/>
          </div>
          <span class="ms-count">{{ m.count }}次</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <span>{{ syncTime ? 'SYNC ' + syncTime : '' }}</span>
      <span v-if="error" class="err">{{ error }}</span>
    </div>
  </div>
</template>

<style scoped>
.panel { background: rgba(15,23,42,0.55); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(148,163,184,0.08); border-radius: 16px; padding: 18px 20px; width: 240px; height: 440px; display: flex; flex-direction: column; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.panel-title { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; font-size: 13px; font-weight: 600; color: #e2e8f0; letter-spacing: 0.3px; }
.drag-handle { -webkit-app-region: drag; }
.title-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.title-dot.blue { background: #3b82f6; box-shadow: 0 0 8px rgba(59,130,246,0.5); }
.section { margin-bottom: 12px; }
.label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.balance-row { display: flex; align-items: baseline; gap: 10px; }
.balance-num { font-size: 30px; font-weight: 700; color: #60a5fa; font-family: 'Consolas',monospace; letter-spacing: -1px; }
.badge { font-size: 9px; padding: 1px 6px; border-radius: 3px; }
.badge.success { color: #22c55e; background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2); }
.badge.error { color: #ef4444; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); }
.sub-row { display: flex; justify-content: space-between; padding: 2px 0; }
.sub-label { font-size: 10px; color: #64748b; }
.sub-val { font-size: 10px; color: #94a3b8; font-family: 'Consolas',monospace; }
.sub-val.topped { color: #e2e8f0; }
.spend-row { display: flex; align-items: baseline; }
.spend-num { font-size: 22px; font-weight: 700; color: #fbbf24; font-family: 'Consolas',monospace; }
.chart-section { margin-bottom: 8px; }
.mini-chart-wrap { margin-top: 4px; height: 40px; }
.model-summary { display: flex; flex-direction: column; gap: 6px; }
.ms-row { display: flex; align-items: center; gap: 8px; }
.ms-name { font-size: 11px; font-weight: 600; width: 50px; }
.ms-track { flex: 1; height: 4px; background: rgba(148,163,184,0.08); border-radius: 4px; overflow: hidden; }
.ms-fill { height: 100%; border-radius: 4px; transition: width 0.6s; }
.ms-count { font-size: 10px; color: #64748b; font-family: 'Consolas',monospace; min-width: 36px; text-align: right; }
.footer { display: flex; justify-content: space-between; font-size: 9px; color: #475569; margin-top: auto; }
.err { color: #ef4444; }
</style>
