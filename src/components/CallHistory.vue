<script setup>
defineProps({
  calls: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="section">
    <div class="section-title">RECENT CALLS</div>
    <div v-if="!calls.length" class="empty">暂无调用记录</div>
    <div v-for="(call, i) in calls.slice(0, 3)" :key="i" class="row">
      <span class="model">{{ call.model_name }}</span>
      <span class="tokens">{{ (call.token_count || 0).toLocaleString() }}</span>
      <span class="time">{{ call.time_ago || '' }}</span>
    </div>
  </div>
</template>

<style scoped>
.section {
  margin-bottom: 4px;
}
.section-title {
  color: #64748b;
  font-size: 9px;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.empty {
  color: #475569;
  font-size: 10px;
  padding: 8px 0;
}
.row {
  background: #0e1223;
  border-radius: 5px;
  padding: 6px 10px;
  margin-bottom: 3px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.model {
  color: #94a3b8;
  font-size: 10px;
  font-family: monospace;
}
.tokens {
  color: #059669;
  font-size: 10px;
  font-family: monospace;
}
.time {
  color: #475569;
  font-size: 9px;
  font-family: monospace;
}
</style>
