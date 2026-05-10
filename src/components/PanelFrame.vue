<script setup>
import BalanceCard from './BalanceCard.vue'
import ModelSelector from './ModelSelector.vue'
import TokenChart from './TokenChart.vue'
import CallHistory from './CallHistory.vue'

defineProps({
  balance: Object,
  balanceInfo: Object,
  totalBalance: Number,
  models: Array,
  error: String,
  syncTime: String,
  dailyTokens: Number,
  dailySessions: Number,
  estimatedDays: Number,
  weeklySummary: Array,
  recentCalls: Array,
})
defineEmits(['refresh'])
</script>

<template>
  <div class="panel">
    <!-- Header (draggable) -->
    <div class="header">
      <div class="header-left">
        <span class="status-dot" :class="error ? 'error' : 'ok'">●</span>
        <span class="title">TOKEN SURVEILLANCE</span>
      </div>
      <span class="sync-time">{{ syncTime }}</span>
    </div>

    <div class="divider" />

    <div class="content">
      <BalanceCard
        :balance-info="balanceInfo"
        :total-balance="totalBalance"
        :daily-tokens="dailyTokens"
        :daily-sessions="dailySessions"
        :estimated-days="estimatedDays"
      />
      <ModelSelector :models="models" />
      <TokenChart :summaries="weeklySummary" />
      <CallHistory :calls="recentCalls" />
    </div>

    <!-- Footer -->
    <div class="footer">
      <span class="api-status" :class="error ? 'error' : 'ok'">
        DeepSeek API · {{ error || 'Connected' }}
      </span>
      <button class="refresh-btn" @click="$emit('refresh')">⟳ Refresh</button>
    </div>
  </div>
</template>

<style scoped>
.panel {
  width: 320px;
  background: #020617;
  border: 1px solid #1E293B;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: move;
  -webkit-app-region: drag;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-dot.ok {
  color: #22c55e;
  font-size: 10px;
}
.status-dot.error {
  color: #ef4444;
  font-size: 10px;
}
.title {
  color: #f1f5f9;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
}
.sync-time {
  color: #475569;
  font-size: 9px;
  font-family: monospace;
}
.divider {
  height: 1px;
  background: #1e293b;
  margin: 0 12px;
}
.content {
  padding: 10px 14px;
}
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px 12px;
}
.api-status {
  font-size: 9px;
}
.api-status.ok {
  color: #475569;
}
.api-status.error {
  color: #ef4444;
}
.refresh-btn {
  color: #64748b;
  font-size: 9px;
  font-family: monospace;
  border: 1px solid #1e293b;
  border-radius: 4px;
  padding: 4px 10px;
  background: transparent;
  cursor: pointer;
}
.refresh-btn:hover {
  color: #94a3b8;
  border-color: #334155;
}
</style>
