# Token Surveillance — Electron + Vue 3 实现计划

> **For agentic workers:** 使用 `subagent-driven-development` 或 `executing-plans` 按任务执行。

**Goal:** 用 Electron + Vue 3 重写 Token Surveillance，替代 PyQt5 版本

**Architecture:** Electron main process 管理系统托盘和窗口 IPC；Vue 3 渲染器进程负责 UI；DeepSeek API 通过 IPC bridge 调用，结果缓存在 renderer 的 Pinia store 中。

**Tech Stack:** Electron 33, Vue 3 (Composition API), Vite, ECharts, Tailwind CSS, Pinia

---

### Task 1: 项目脚手架

**Files:**
- Create: `package.json`
- Create: `vite.config.js`
- Create: `index.html`
- Create: `electron/main.js`
- Create: `electron/preload.js`
- Create: `src/main.js`
- Create: `src/App.vue`

- [ ] **Step 1: 初始化项目**

```bash
cd "E:\SparkHub\Token Surveillance"
npm init -y
npm install vue@3 pinia echarts vue-echarts electron@latest electron-builder --save
npm install -D vite @vitejs/plugin-vue concurrently wait-on
```

- [ ] **Step 2: 创建 vite.config.js**

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: './',
  build: { outDir: 'dist' }
})
```

- [ ] **Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    body { background: #020617; font-family: 'Segoe UI', system-ui, sans-serif; }
  </style>
  <title>Token Surveillance</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 electron/main.js**

```js
const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron')
const path = require('path')

let tray = null
let win = null
let isQuitting = false
let trayIcon = null

function createTrayIcon() {
  const size = 32
  const canvas = nativeImage.createEmpty()
  // Generate a simple 32x32 green circle with "S"
  // For now use a solid green pixel icon
  const icon = nativeImage.createFromBuffer(
    Buffer.alloc(size * size * 4, 0), // RGBA placeholder
    { width: size, height: size }
  )
  return icon
}

function createWindow() {
  win = new BrowserWindow({
    width: 340,
    height: 420,
    frame: false,
    transparent: true,
    resizable: false,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
  })

  win.on('blur', () => {
    if (!isQuitting) win.hide()
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }
}

function createTray() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.png')
  tray = new Tray(iconPath)
  tray.setToolTip('Token Surveillance')

  const contextMenu = Menu.buildFromTemplate([
    { label: '显示面板', click: () => win && (win.isVisible() ? win.hide() : win.show()) },
    { type: 'separator' },
    { label: '退出', click: () => { isQuitting = true; app.quit() } }
  ])
  tray.setContextMenu(contextMenu)
  tray.on('click', () => win && (win.isVisible() ? win.hide() : win.show()))
}

app.whenReady().then(() => {
  createWindow()
  createTray()
})

app.on('before-quit', () => { isQuitting = true })

app.on('window-all-closed', () => {})
```

- [ ] **Step 5: 创建 electron/preload.js**

```js
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  fetchBalance: () => ipcRenderer.invoke('fetch-balance'),
  fetchModels: () => ipcRenderer.invoke('fetch-models'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  getWeeklySummary: () => ipcRenderer.invoke('get-weekly-summary'),
})
```

- [ ] **Step 6: 创建 src/main.js**

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
```

- [ ] **Step 7: 更新 package.json scripts**

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "electron:dev": "concurrently \"vite\" \"wait-on http://localhost:5173 && electron .\"",
  "electron:build": "vite build && electron-builder"
}
```

---

### Task 2: Electron Main Process — 系统托盘 + IPC 处理

**Files:**
- Modify: `electron/main.js`
- Create: `src/api.js` (renderer-side API)
- Create: `src/stores/app.js` (Pinia store)

- [ ] **Step 1: 扩展 electron/main.js 添加 IPC 处理器**

在 `electron/main.js` 中 `createWindow()` 之后加入：

```js
const https = require('https')

let configStore = { apiKey: '', balanceThreshold: 10.0 }

ipcMain.handle('get-config', () => configStore)

ipcMain.handle('save-config', (_, config) => {
  configStore = { ...configStore, ...config }
  return true
})

ipcMain.handle('fetch-balance', async () => {
  if (!configStore.apiKey) return { error: 'API Key 未设置' }
  try {
    const data = await httpsGet('/user/balance', configStore.apiKey)
    return { data }
  } catch (e) { return { error: e.message } }
})

ipcMain.handle('fetch-models', async () => {
  if (!configStore.apiKey) return { error: 'API Key 未设置' }
  try {
    const data = await httpsGet('/v1/models', configStore.apiKey)
    return { data }
  } catch (e) { return { error: e.message } }
})

function httpsGet(endpoint, apiKey) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://api.deepseek.com${endpoint}`)
    const req = https.get(url, { headers: { 'Authorization': `Bearer ${apiKey}`, 'Accept': 'application/json' } }, res => {
      let body = ''
      res.on('data', c => body += c)
      res.on('end', () => {
        if (res.statusCode >= 400) reject(new Error(`HTTP ${res.statusCode}`))
        else resolve(JSON.parse(body))
      })
    })
    req.on('error', reject)
    req.setTimeout(10000, () => { req.destroy(); reject(new Error('请求超时')) })
  })
}
```

- [ ] **Step 2: 创建 src/stores/app.js (Pinia store)**

```js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const balance = ref(null)
  const models = ref([])
  const error = ref('')
  const syncTime = ref('')

  async function refresh() {
    const [balResult, modResult] = await Promise.all([
      window.electronAPI.fetchBalance(),
      window.electronAPI.fetchModels()
    ])

    if (balResult.data) {
      balance.value = balResult.data
      error.value = ''
    } else {
      error.value = balResult.error
    }

    if (modResult.data && modResult.data.data) {
      models.value = modResult.data.data
    }

    syncTime.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return { balance, models, error, syncTime, refresh }
})
```

---

### Task 3: Vue 前端 — App + 面板框架

**Files:**
- Create: `src/App.vue`
- Create: `src/components/PanelFrame.vue`

- [ ] **Step 1: 创建 App.vue**

```vue
<script setup>
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/app'
import PanelFrame from './components/PanelFrame.vue'

const store = useAppStore()
const showPanel = ref(false)

onMounted(async () => {
  await store.refresh()
  showPanel.value = true
})

function refresh() { store.refresh() }
</script>

<template>
  <div class="panel-container">
    <PanelFrame
      v-if="showPanel"
      :balance="store.balance"
      :models="store.models"
      :error="store.error"
      :sync-time="store.syncTime"
      @refresh="refresh"
    />
  </div>
</template>

<style>
.panel-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  -webkit-app-region: drag;  /* 窗口拖拽 */
}
</style>
```

- [ ] **Step 2: 创建 src/components/PanelFrame.vue**

```vue
<script setup>
defineProps({
  balance: Object, models: Array, error: String, syncTime: String
})
defineEmits(['refresh'])
</script>

<template>
  <div class="panel">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <span class="status-dot" :class="error ? 'error' : 'ok'">●</span>
        <span class="title">TOKEN SURVEILLANCE</span>
      </div>
      <span class="sync-time">{{ syncTime }}</span>
    </div>

    <div class="divider" />

    <div class="content">
      <!-- 这里后续 Task 会填充组件 -->
      <div class="placeholder">Loading...</div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <span class="api-status" :class="error ? 'error' : 'ok'">
        DeepSeek API · {{ error ? 'Error' : 'Connected' }}
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
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  overflow: hidden;
  -webkit-app-region: no-drag;
}
.header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; cursor: move;
}
.header-left { display: flex; align-items: center; gap: 6px; }
.status-dot.ok { color: #22C55E; font-size: 10px; }
.status-dot.error { color: #EF4444; font-size: 10px; }
.title { color: #F1F5F9; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; }
.sync-time { color: #475569; font-size: 9px; font-family: monospace; }
.divider { height: 1px; background: #1E293B; margin: 0 12px; }
.content { padding: 12px 16px; min-height: 200px; }
.placeholder { color: #475569; text-align: center; padding: 40px 0; }
.footer {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 16px 12px;
}
.api-status { font-size: 9px; }
.api-status.ok { color: #475569; }
.api-status.error { color: #EF4444; }
.refresh-btn {
  color: #64748B; font-size: 9px; font-family: monospace;
  border: 1px solid #1E293B; border-radius: 4px;
  padding: 4px 10px; background: transparent; cursor: pointer;
}
.refresh-btn:hover { color: #94A3B8; border-color: #334155; }
</style>
```

---

### Task 4: Vue 前端 — 余额卡片组件

**Files:**
- Create: `src/components/BalanceCard.vue`

- [ ] **Step 1: 创建 BalanceCard.vue**

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  balance: Object
})

const info = computed(() => {
  if (!props.balance?.balance_infos?.length) return null
  return props.balance.balance_infos[0]
})

const borderColor = computed(() => {
  if (!info.value) return '#059669'
  const b = parseFloat(info.value.total_balance)
  if (b < 1) return '#EF4444'
  if (b < 10) return '#D97706'
  return '#059669'
})
</script>

<template>
  <div class="balance-card" :style="{ borderLeftColor: borderColor }">
    <div class="card-header">
      <span class="card-label">BALANCE</span>
      <span class="card-badge">DeepSeek</span>
    </div>
    <div class="amount">
      {{ info ? `¥${parseFloat(info.total_balance).toFixed(2)}` : '--' }}
    </div>
    <div class="info-row">
      Today -- tok · -- sessions · Est. --d
    </div>
  </div>
</template>

<style scoped>
.balance-card {
  background: #0E1223;
  border-left: 3px solid v-bind(borderColor);
  border-radius: 8px;
  border: 1px solid #1E293B;
  padding: 12px 14px;
  margin-bottom: 8px;
}
.card-header { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.card-label { color: #64748B; font-size: 9px; letter-spacing: 1.5px; }
.card-badge {
  color: #059669; font-size: 8px; border: 1px solid #05966940;
  border-radius: 3px; padding: 1px 6px; background: #05966910;
}
.amount {
  color: #F1F5F9; font-size: 36px; font-weight: 800;
  font-family: 'Consolas', monospace;
}
.info-row { color: #64748B; font-size: 10px; margin-top: 2px; }
</style>
```

---

### Task 5: Vue 前端 — 模型选择器组件

**Files:**
- Create: `src/components/ModelSelector.vue`

- [ ] **Step 1: 创建 ModelSelector.vue**

```vue
<script setup>
import { ref } from 'vue'

const props = defineProps({ models: Array })
const selected = ref('')

function select(id) { selected.value = id }
</script>

<template>
  <div class="selector">
    <button
      v-for="m in models" :key="m.id"
      :class="['model-btn', { active: selected === m.id }]"
      @click="select(m.id)"
    >
      {{ m.id }}
    </button>
  </div>
</template>

<style scoped>
.selector { display: flex; gap: 6px; margin-bottom: 8px; }
.model-btn {
  flex: 1; background: #0E1223; color: #94A3B8;
  border: 1px solid transparent; border-radius: 5px;
  padding: 6px 10px; font-size: 10px; font-family: monospace;
  cursor: pointer; opacity: 0.6;
}
.model-btn:hover { border-color: #059669; opacity: 0.8; }
.model-btn.active { border-color: #059669; opacity: 1; color: #E2E8F0; }
</style>
```

---

### Task 6: Vue 前端 — Token 柱状图组件 (ECharts)

**Files:**
- Create: `src/components/TokenChart.vue`

- [ ] **Step 1: 创建 TokenChart.vue**

```vue
<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import 'echarts'

const props = defineProps({
  summaries: { type: Array, default: () => generateEmptyData() }
})

function generateEmptyData() {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push({ date: d.toISOString().slice(0, 10), total_tokens: 0 })
  }
  return days
}

const option = computed(() => ({
  grid: { left: 0, right: 0, top: 4, bottom: 16, containLabel: true },
  xAxis: {
    type: 'category',
    data: props.summaries.map(s => s.date.slice(5)),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#64748B', fontSize: 8, fontFamily: 'monospace' },
  },
  yAxis: {
    type: 'value', show: false,
    splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
  },
  series: [{
    type: 'bar',
    data: props.summaries.map((s, i) => ({
      value: s.total_tokens,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#059669' },
          { offset: 1, color: '#05966920' }
        ]),
        borderRadius: [3, 3, 0, 0],
      }
    })),
    barWidth: '70%',
  }],
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0E1223',
    borderColor: '#1E293B',
    textStyle: { color: '#E2E8F0', fontSize: 10, fontFamily: 'monospace' },
    formatter: ({ name, value }) => `${name}<br/>Tokens: ${value?.toLocaleString() || 0}`,
  },
}))
</script>

<template>
  <div class="chart-wrapper">
    <div class="chart-title">7-DAY TOKEN USAGE</div>
    <VChart :option="option" autoresize class="chart" />
  </div>
</template>

<style scoped>
.chart-wrapper { background: #0E1223; border-radius: 6px; padding: 10px 8px; margin-bottom: 8px; }
.chart-title { color: #64748B; font-size: 9px; letter-spacing: 1px; margin-bottom: 4px; }
.chart { height: 100px; width: 100%; }
</style>
```

---

### Task 7: 组装所有组件 + 完善样式

**Files:**
- Modify: `src/components/PanelFrame.vue`

- [ ] **Step 1: 更新 PanelFrame.vue 使用所有子组件**

```vue
<script setup>
import BalanceCard from './BalanceCard.vue'
import ModelSelector from './ModelSelector.vue'
import TokenChart from './TokenChart.vue'

defineProps({
  balance: Object, models: Array, error: String, syncTime: String
})
defineEmits(['refresh'])
</script>

<template>
  <div class="panel">
    <div class="header">
      <div class="header-left">
        <span class="status-dot" :class="error ? 'error' : 'ok'">●</span>
        <span class="title">TOKEN SURVEILLANCE</span>
      </div>
      <span class="sync-time">{{ syncTime }}</span>
    </div>
    <div class="divider" />

    <div class="content">
      <BalanceCard :balance="balance" />
      <ModelSelector :models="models" />
      <TokenChart />
    </div>

    <div class="footer">
      <span class="api-status" :class="error ? 'error' : 'ok'">
        DeepSeek API · {{ error ? error : 'Connected' }}
      </span>
      <button class="refresh-btn" @click="$emit('refresh')">⟳ Refresh</button>
    </div>
  </div>
</template>
```

---

### Task 8: API Key 输入 + 持久化存储

**Files:**
- Create: `src/components/SetupDialog.vue`
- Modify: `src/App.vue`

- [ ] **Step 1: 创建 SetupDialog.vue**

```vue
<script setup>
import { ref } from 'vue'

const emit = defineEmits(['confirm'])
const key = ref('')

function submit() {
  if (key.value.trim()) emit('confirm', key.value.trim())
}
</script>

<template>
  <div class="setup-overlay">
    <div class="setup-dialog">
      <h2>Token Surveillance</h2>
      <p>请输入 DeepSeek API Key 以开始使用</p>
      <input v-model="key" type="password" placeholder="sk-..." @keyup.enter="submit" />
      <button @click="submit" :disabled="!key.trim()">确认</button>
    </div>
  </div>
</template>

<style scoped>
.setup-overlay {
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: #020617;
}
.setup-dialog {
  background: #0E1223; border: 1px solid #1E293B; border-radius: 10px;
  padding: 32px; width: 300px; text-align: center;
}
h2 { color: #F1F5F9; font-size: 16px; margin: 0 0 8px; }
p { color: #94A3B8; font-size: 12px; margin: 0 0 16px; }
input {
  width: 100%; box-sizing: border-box;
  background: #020617; border: 1px solid #334155; border-radius: 6px;
  padding: 8px 12px; color: #E2E8F0; font-size: 12px; margin-bottom: 12px;
  outline: none;
}
input:focus { border-color: #059669; }
button {
  background: #059669; color: #fff; border: none; border-radius: 6px;
  padding: 8px 24px; font-size: 12px; cursor: pointer;
}
button:disabled { opacity: 0.4; cursor: default; }
</style>
```

- [ ] **Step 2: 更新 App.vue 集成 SetupDialog**

```vue
<script setup>
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/app'
import PanelFrame from './components/PanelFrame.vue'
import SetupDialog from './components/SetupDialog.vue'

const store = useAppStore()
const showPanel = ref(false)
const needsSetup = ref(false)

onMounted(async () => {
  const config = await window.electronAPI.getConfig()
  if (!config.apiKey) {
    needsSetup.value = true
    return
  }
  await store.refresh()
  showPanel.value = true
})

async function onKeyConfirm(key) {
  await window.electronAPI.saveConfig({ apiKey: key })
  needsSetup.value = false
  await store.refresh()
  showPanel.value = true
}

function refresh() { store.refresh() }
</script>

<template>
  <div class="panel-container">
    <SetupDialog v-if="needsSetup" @confirm="onKeyConfirm" />
    <PanelFrame v-else-if="showPanel" ... />
  </div>
</template>
```

---

### Task 9: 图标 + 打包配置

**Files:**
- Create: `public/icon.png` (从现有 assets 复制)
- Create: `electron-builder.yml`

- [ ] **Step 1: 复制图标**

```bash
cp "E:\SparkHub\Token Surveillance\assets\icon.png" "E:\SparkHub\Token Surveillance\public\icon.png"
```

- [ ] **Step 2: 创建 electron-builder.yml**

```yaml
appId: com.tokensurveillance.app
productName: Token Surveillance
directories:
  output: release
files:
  - dist
  - electron
  - public
win:
  target: portable
  icon: public/icon.png
```

- [ ] **Step 3: 创建 .gitignore**

```
node_modules/
dist/
release/
.DS_Store
```

---

## 验证步骤

1. `npm run electron:dev` — 开发模式启动，窗口 + 托盘出现
2. 首次运行弹出 API Key 输入框
3. 面板自动显示余额和模型列表
4. 柱状图渲染 7 天数据
5. 托盘右键菜单正常
6. 点击面板外部自动隐藏
7. `npm run electron:build` — 打包为 exe
