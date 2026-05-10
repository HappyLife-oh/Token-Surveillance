<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import { useAppStore } from './stores/app'
import AccountPanel from './components/AccountPanel.vue'
import MonitorPanel from './components/MonitorPanel.vue'
import SetupDialog from './components/SetupDialog.vue'

const store = useAppStore()
const ready = ref(false)
const needsSetup = ref(false)

onMounted(async () => {
  const config = await window.electronAPI.getConfig()
  if (!config.apiKey) {
    needsSetup.value = true
    return
  }
  // Pre-refresh balance (silent fetch via main process)
  try { await window.electronAPI.ensureRefreshed() } catch (_) {}
  await store.refresh()
  ready.value = true
})

async function onKeyConfirm(key) {
  await window.electronAPI.saveConfig({ apiKey: key })
  needsSetup.value = false
  await store.refresh()
  ready.value = true
}

async function refresh() {
  try { await window.electronAPI.ensureRefreshed() } catch (_) {}
  store.refresh()
}

// Auto-poll every 5 minutes
let pollTimer = null
onMounted(() => {
  pollTimer = setInterval(refresh, 5 * 60 * 1000)
})
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="app">
    <SetupDialog v-if="needsSetup" @confirm="onKeyConfirm" />

    <template v-if="!needsSetup && !ready">
      <div class="loading-state">
        <div class="loading-spinner" />
        <div class="loading-text">Connecting to DeepSeek API...</div>
      </div>
    </template>

    <template v-if="ready">
      <div class="bg" />
      <div class="orb orb-1" />
      <div class="orb orb-2" />

      <div class="dashboard">
        <!-- Left: Account Overview -->
        <AccountPanel
          :total-balance="store.totalBalance"
          :granted-balance="store.grantedBalance"
          :topped-up-balance="store.toppedUpBalance"
          :is-available="store.isAvailable"
          :monthly-spending="store.monthlySpending"
          :model-breakdown="store.modelBreakdown"
          :balance-trend="store.balanceTrend"
          :sparkline-data="store.sparklineData"
          :sync-time="store.syncTime"
          :error="store.error"
        />

        <!-- Center: Model Comparison & Frequency -->
        <MonitorPanel
          :model-breakdown="store.modelBreakdown"
          :daily-requests="store.dailyRequests"
          :daily-composition="store.dailyTokenComposition"
          :total-calls="store.totalCalls"
          :total-tokens="store.totalTokensAll"
          :sync-time="store.syncTime"
          :error="store.error"
          @refresh="refresh"
        />

        <!-- Right: Stats & Chart -->
        <div class="panel right-panel">
          <div class="panel-title drag-handle">
            <div class="title-dot purple" />
            <span>深度求索</span>
          </div>

          <!-- Stat cards -->
          <div class="stat-row">
            <div class="stat-card">
              <div class="stat-icon blue">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </div>
              <div class="stat-info">
                <div class="stat-label">总调用次数</div>
                <div class="stat-value">{{ (store.totalCalls || 0).toLocaleString() }}</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon green">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
              </div>
              <div class="stat-info">
                <div class="stat-label">总 Token 消耗</div>
                <div class="stat-value">{{ (store.totalTokensAll / 1e6).toFixed(2) }}M</div>
              </div>
            </div>
            <button class="refresh-icon" @click="refresh" title="刷新">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            </button>
          </div>

          <!-- Token composition stacked bar -->
          <div class="chart-box">
            <div class="section-label">Token 构成 <span class="label-hint">缓存/未缓存/输出</span></div>
            <!-- Model filter tabs -->
            <div class="filter-tabs">
              <button
                v-for="m in store.modelOptions"
                :key="m"
                :class="['filter-tab', { active: (store.selectedModel || 'all') === m }]"
                @click="store.selectedModel = m === 'all' ? null : m"
              >
                {{ m === 'all' ? 'ALL' : m.includes('flash') ? 'V4 Flash' : 'V4 Pro' }}
              </button>
            </div>
            <div class="chart-container">
              <StackedBar :data="store.dailyTokenComposition" />
            </div>
          </div>

          <!-- Status -->
          <div v-if="store.error" class="status error">DeepSeek API · {{ store.error }}</div>
          <div v-else class="status ok">
            <span>DeepSeek API · Connected</span>
            <span class="sync-info">{{ store.syncTime ? 'SYNC ' + store.syncTime : '' }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import StackedBar from './components/StackedBar.vue'
export default { components: { StackedBar } }
</script>

<style>
/* Reset & Base */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  width: 100%; height: 100%; overflow: hidden;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: transparent;
}

.app { width: 100vw; height: 100vh; position: relative; display: flex; align-items: center; justify-content: center; background: transparent; overflow: hidden; }

/* Background layers */
.bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 800px 500px at 20% 60%, rgba(30,58,138,0.25) 0%, transparent 60%),
    radial-gradient(ellipse 600px 400px at 80% 40%, rgba(15,23,42,0.5) 0%, transparent 50%),
    linear-gradient(175deg, #020617 0%, #0f172a 35%, #1e293b 65%, #0f172a 100%);
  z-index: 0;
}
.orb { position: absolute; border-radius: 50%; filter: blur(80px); z-index: 0; pointer-events: none; }
.orb-1 { width: 300px; height: 300px; background: rgba(59,130,246,0.08); top: -60px; left: 5%; }
.orb-2 { width: 250px; height: 250px; background: rgba(139,92,246,0.06); bottom: -40px; right: 10%; }

/* Dashboard */
.dashboard { position: relative; z-index: 1; display: flex; gap: 12px; padding: 16px; width: 100%; height: 100%; align-items: center; justify-content: center; }

/* Glass panel base */
.panel {
  background: rgba(15,23,42,0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(148,163,184,0.08);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s ease;
}
.panel:hover { border-color: rgba(148,163,184,0.12); }
.right-panel { width: 340px; height: 440px; }

/* Panel titles */
.panel-title { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 13px; font-weight: 600; color: #e2e8f0; letter-spacing: 0.3px; }
.drag-handle { -webkit-app-region: drag; }
.panel-title button, .panel-title .filter-tab { -webkit-app-region: no-drag; }
.title-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.title-dot.purple { background: #8b5cf6; box-shadow: 0 0 8px rgba(139,92,246,0.5); }

/* Stat cards */
.stat-row { display: flex; gap: 8px; margin-bottom: 14px; align-items: center; }
.stat-card {
  flex: 1;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(148,163,184,0.06);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: border-color 0.2s ease, background 0.2s ease;
  cursor: default;
}
.stat-card:hover { border-color: rgba(148,163,184,0.15); background: rgba(15,23,42,0.55); }
.stat-icon {
  width: 34px; height: 34px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: transform 0.15s ease;
}
.stat-card:hover .stat-icon { transform: scale(1.05); }
.stat-icon.blue { background: rgba(59,130,246,0.12); color: #60a5fa; }
.stat-icon.green { background: rgba(34,197,94,0.12); color: #22c55e; }
.stat-label { font-size: 9px; color: #64748b; font-weight: 500; margin-bottom: 2px; }
.stat-value { font-size: 15px; font-weight: 700; color: #e2e8f0; font-family: 'Inter', 'Consolas', monospace; }
.refresh-icon {
  background: rgba(148,163,184,0.08);
  border: 1px solid rgba(148,163,184,0.1);
  color: #94a3b8;
  border-radius: 8px;
  padding: 9px;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.refresh-icon:hover { background: rgba(59,130,246,0.15); border-color: #3b82f6; color: #60a5fa; transform: rotate(180deg); }

/* Chart section */
.chart-box { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.section-label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; font-weight: 500; }
.label-hint { color: #475569; font-size: 8px; text-transform: none; letter-spacing: 0; font-weight: 400; }
.chart-container { flex: 1; min-height: 0; width: 100%; }

/* Status bar */
.status { display: flex; justify-content: space-between; margin-top: 8px; font-size: 9px; }
.status.ok { color: #475569; letter-spacing: 0.2px; }
.status.error { color: #ef4444; }
.sync-info { color: #334155; }

/* Model filter tabs */
.filter-tabs { display: flex; gap: 4px; margin-bottom: 8px; }
.filter-tab {
  background: rgba(148,163,184,0.06);
  border: 1px solid rgba(148,163,184,0.1);
  color: #64748b;
  border-radius: 4px;
  padding: 3px 12px;
  font-size: 9px;
  cursor: pointer;
  font-family: 'Inter', 'Consolas', monospace;
  transition: all 0.15s ease;
  font-weight: 500;
}
.filter-tab:hover { border-color: #3b82f6; color: #94a3b8; background: rgba(59,130,246,0.06); }
.filter-tab.active { background: rgba(59,130,246,0.12); border-color: #3b82f6; color: #60a5fa; font-weight: 600; }

/* Loading skeleton */
.loading-state {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 16px; z-index: 10;
}
.loading-spinner {
  width: 28px; height: 28px;
  border: 2.5px solid rgba(59,130,246,0.15);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.loading-text { color: #64748b; font-size: 12px; font-weight: 400; letter-spacing: 0.3px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
