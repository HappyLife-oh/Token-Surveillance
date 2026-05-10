<script setup>
defineProps({
  breakdown: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="comparison">
    <div class="section-title">模型对比 · 调用频率与资源消耗</div>

    <div class="model-cards">
      <div v-for="m in breakdown" :key="m.id" class="model-card" :style="{ borderTopColor: m.color }">
        <div class="mc-header">
          <span class="mc-name" :style="{ color: m.color }">{{ m.label }}</span>
          <span class="mc-badge">{{ m.count }} 次</span>
        </div>
        <div class="mc-stats">
          <div class="mc-stat">
            <span class="mc-label">调用次数</span>
            <span class="mc-val">{{ m.count.toLocaleString() }}</span>
          </div>
          <div class="mc-stat">
            <span class="mc-label">Token 消耗</span>
            <span class="mc-val">{{ (m.tokens / 1e6).toFixed(2) }}M</span>
          </div>
          <div class="mc-stat">
            <span class="mc-label">占比</span>
            <span class="mc-val">{{ m.count > 0 && breakdown[0]?.count > 0 ? Math.round(m.count / breakdown.reduce((s,x) => s + x.count, 0) * 100) : 0 }}%</span>
          </div>
        </div>
        <!-- Mini bar -->
        <div class="mini-track">
          <div
            class="mini-fill"
            :style="{
              width: (breakdown[0]?.count ? (m.count / breakdown.reduce((s,x) => s + x.count, 0) * 100) : 0) + '%',
              background: m.color,
              boxShadow: '0 0 6px ' + m.glow,
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comparison { margin-bottom: 12px; }
.section-title { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.model-cards { display: flex; flex-direction: column; gap: 10px; }
.model-card {
  background: rgba(15,23,42,0.5); border: 1px solid rgba(148,163,184,0.06);
  border-top: 2px solid; border-radius: 10px; padding: 12px 14px;
}
.mc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.mc-name { font-size: 13px; font-weight: 700; }
.mc-badge { font-size: 9px; color: #64748b; background: rgba(148,163,184,0.08); border-radius: 4px; padding: 2px 8px; }
.mc-stats { display: flex; gap: 16px; margin-bottom: 8px; }
.mc-stat { flex: 1; }
.mc-label { display: block; font-size: 9px; color: #64748b; }
.mc-val { display: block; font-size: 16px; font-weight: 700; color: #e2e8f0; font-family: 'Consolas',monospace; }
.mini-track { height: 3px; background: rgba(148,163,184,0.08); border-radius: 3px; overflow: hidden; }
.mini-fill { height: 100%; border-radius: 3px; transition: width 0.6s; }
</style>
