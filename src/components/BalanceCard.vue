<script setup>
import { computed } from 'vue'

const props = defineProps({
  balanceInfo: Object,
  totalBalance: Number,
  dailyTokens: Number,
  dailySessions: Number,
  estimatedDays: Number,
})

const borderColor = computed(() => {
  const b = props.totalBalance
  if (b < 1) return '#EF4444'
  if (b < 10) return '#D97706'
  return '#059669'
})

const balanceStr = computed(() => {
  return props.totalBalance ? `¥${props.totalBalance.toFixed(2)}` : '--'
})

const tokensStr = computed(() => {
  const t = props.dailyTokens || 0
  if (t >= 1e6) return `${(t / 1e6).toFixed(2)}M`
  return t.toLocaleString()
})
</script>

<template>
  <div class="card" :style="{ borderLeftColor: borderColor }">
    <div class="card-header">
      <span class="label">BALANCE</span>
      <span v-if="balanceInfo" class="pill"
        >DeepSeek · {{ balanceInfo.currency }}</span
      >
    </div>
    <div class="amount">{{ balanceStr }}</div>
    <div class="info">
      Today {{ tokensStr }} tok · {{ dailySessions || '--' }} sessions · Est.
      ~{{ estimatedDays || '--' }}d
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #0e1223;
  border-left: 3px solid v-bind(borderColor);
  border-radius: 8px;
  border: 1px solid #1e293b;
  padding: 12px 14px;
  margin-bottom: 8px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.label {
  color: #64748b;
  font-size: 9px;
  letter-spacing: 1.5px;
}
.pill {
  color: #059669;
  font-size: 8px;
  letter-spacing: 0.5px;
  border: 1px solid #05966940;
  border-radius: 3px;
  padding: 1px 6px;
  background: #05966910;
}
.amount {
  color: #f1f5f9;
  font-size: 36px;
  font-weight: 800;
  font-family: "Consolas", monospace;
}
.info {
  color: #64748b;
  font-size: 10px;
  margin-top: 2px;
}
</style>
