const { app, BrowserWindow, Tray, Menu, ipcMain, screen } = require('electron')
const path = require('path')
const fs = require('fs')
const https = require('https')
const { fork } = require('child_process')

let proxyProcess = null
let tray = null
let win = null
let isQuitting = false
const USER_DATA = app.getPath('userData')

// ============================================================
// Config
// ============================================================
const CONFIG_PATH = path.join(USER_DATA, 'config.json')
let configStore = {}
try { if (fs.existsSync(CONFIG_PATH)) configStore = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8')) } catch (_) {}
if (!configStore.apiKey) configStore = { apiKey: '', balanceThreshold: 10.0 }
function saveConfig() {
  fs.mkdirSync(path.dirname(CONFIG_PATH), { recursive: true })
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(configStore, null, 2))
}

// ============================================================
// Balance history (API snapshots)
// ============================================================
const HISTORY_PATH = path.join(USER_DATA, 'balance_history.json')
let balanceHistory = []
try { if (fs.existsSync(HISTORY_PATH)) balanceHistory = JSON.parse(fs.readFileSync(HISTORY_PATH, 'utf-8')) } catch (_) {}
if (!Array.isArray(balanceHistory)) balanceHistory = []
function saveHistory() {
  fs.writeFileSync(HISTORY_PATH, JSON.stringify(balanceHistory, null, 2))
}

// ============================================================
// CSV usage data import
// ============================================================
const CSV_DIR = path.join('E:', 'SparkHub', 'Token Surveillance', 'usage_data_2026_5')

function parseCSV(text) {
  const lines = text.trim().split('\n')
  if (lines.length < 2) return []
  const headers = lines[0].split(',').map((h) => h.trim())
  return lines.slice(1).map((line) => {
    const vals = line.split(',')
    const row = {}
    headers.forEach((h, i) => (row[h] = vals[i]?.trim() || ''))
    return row
  })
}

function loadUsageData() {
  const amountPath = path.join(CSV_DIR, 'amount-2026-5.csv')
  const costPath = path.join(CSV_DIR, 'cost-2026-5.csv')
  let amountRows = []
  let costRows = []

  try {
    if (fs.existsSync(amountPath)) amountRows = parseCSV(fs.readFileSync(amountPath, 'utf-8'))
    if (fs.existsSync(costPath)) costRows = parseCSV(fs.readFileSync(costPath, 'utf-8'))
  } catch (e) {
    console.error('CSV load error:', e.message)
  }

  // Group amount rows by date + model
  const daily = {}
  const dailyCost = {}

  amountRows.forEach((r) => {
    const key = `${r.utc_date}::${r.model}`
    if (!daily[key]) daily[key] = { date: r.utc_date, model: r.model, requests: 0, cached: 0, uncached: 0, output: 0 }
    if (r.type === 'request_count') daily[key].requests += parseInt(r.amount) || 0
    if (r.type === 'input_cache_hit_tokens') daily[key].cached += parseInt(r.amount) || 0
    if (r.type === 'input_cache_miss_tokens') daily[key].uncached += parseInt(r.amount) || 0
    if (r.type === 'output_tokens') daily[key].output += parseInt(r.amount) || 0
  })

  costRows.forEach((r) => {
    const key = `${r.utc_date}::${r.model}`
    if (!dailyCost[key]) dailyCost[key] = { date: r.utc_date, model: r.model, cost: 0 }
    dailyCost[key].cost += parseFloat(r.cost) || 0
  })

  // Merge costs into daily
  Object.keys(dailyCost).forEach((k) => {
    if (daily[k]) daily[k].cost = parseFloat(dailyCost[k].cost.toFixed(4))
  })

  return Object.values(daily).sort((a, b) => a.date.localeCompare(b.date) || a.model.localeCompare(b.model))
}

// ============================================================
// DeepSeek API
// ============================================================
function httpsGet(endpoint, apiKey) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://api.deepseek.com${endpoint}`)
    const req = https.get(url, {
      headers: { Authorization: `Bearer ${apiKey}`, Accept: 'application/json' }
    }, (res) => {
      let body = ''
      res.on('data', (c) => (body += c))
      res.on('end', () => {
        if (res.statusCode >= 400) reject(new Error(`HTTP ${res.statusCode}`))
        else try { resolve(JSON.parse(body)) } catch (_) { reject(new Error('解析失败')) }
      })
    })
    req.on('error', reject)
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('请求超时')) })
  })
}

// ============================================================
// Window (tray-triggered, draggable)
// ============================================================
function positionNearTray() {
  const cursor = screen.getCursorScreenPoint()
  const display = screen.getDisplayNearestPoint(cursor)
  const { x, y, width, height } = display.workArea
  const [wWidth, wHeight] = win.getSize()
  win.setPosition(x + width - wWidth - 20, y + height - wHeight - 48)
}

function createWindow() {
  win = new BrowserWindow({
    width: 820,
    height: 500,
    frame: false,
    transparent: true,
    resizable: false,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  win.on('blur', () => {
    if (!isQuitting) win.hide()
  })

  if (process.env.VITE_DEV_SERVER_URL) win.loadURL(process.env.VITE_DEV_SERVER_URL)
  else win.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
}

// ============================================================
// Tray
// ============================================================
function createTray() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.png')
  tray = new Tray(iconPath)
  tray.setToolTip('Token Surveillance')

  const menu = Menu.buildFromTemplate([
    { label: '显示面板', click: () => { positionNearTray(); win.show() } },
    { type: 'separator' },
    { label: '退出', click: () => { isQuitting = true; app.quit() } },
  ])
  tray.setContextMenu(menu)
  tray.on('click', () => {
    if (win.isVisible()) win.hide()
    else { positionNearTray(); win.show() }
  })

  // Auto-refresh when showing panel
  ipcMain.handle('ensure-refreshed', async () => {
    // Refresh balance silently
    if (configStore.apiKey) {
      try {
        const data = await httpsGet('/user/balance', configStore.apiKey)
        const snap = { time: new Date().toISOString(), total: parseFloat(data.balance_infos?.[0]?.total_balance || 0) }
        balanceHistory.push(snap)
        if (balanceHistory.length > 365) balanceHistory = balanceHistory.slice(-365)
        saveHistory()
      } catch (_) {}
    }
  })
}

// ============================================================
// Proxy subprocess management
// ============================================================
const PROXY_PORT = 18999
const PROXY_SCRIPT = path.join(__dirname, 'proxy-server.js')

function startProxy() {
  if (proxyProcess) return
  const env = { ...process.env, TS_DATA_FILE: path.join(USER_DATA, 'usage_proxy.json') }
  proxyProcess = fork(PROXY_SCRIPT, [], { env, stdio: 'pipe' })
  proxyProcess.stdout?.on('data', (d) => process.stdout.write(`[proxy] ${d}`))
  proxyProcess.stderr?.on('data', (d) => process.stderr.write(`[proxy-err] ${d}`))
  proxyProcess.on('exit', () => { proxyProcess = null })
  console.log(`[TS] Proxy started on :${PROXY_PORT}`)
}

function stopProxy() {
  if (!proxyProcess) return
  proxyProcess.kill()
  proxyProcess = null
  console.log('[TS] Proxy stopped')
}

// ============================================================
// IPC Handlers
// ============================================================
ipcMain.handle('get-config', () => configStore)
ipcMain.handle('save-config', (_, cfg) => {
  Object.assign(configStore, cfg)
  saveConfig()
  return true
})

ipcMain.handle('fetch-balance', async () => {
  if (!configStore.apiKey) return { error: 'API Key 未设置' }
  try {
    const data = await httpsGet('/user/balance', configStore.apiKey)
    const snap = { time: new Date().toISOString(), total: parseFloat(data.balance_infos?.[0]?.total_balance || 0) }
    balanceHistory.push(snap)
    if (balanceHistory.length > 365) balanceHistory = balanceHistory.slice(-365)
    saveHistory()
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

ipcMain.handle('get-balance-history', () => balanceHistory)
ipcMain.handle('get-usage-data', () => loadUsageData())

ipcMain.handle('get-proxy-status', () => ({
  running: proxyProcess !== null,
  port: PROXY_PORT,
}))

ipcMain.handle('get-proxy-usage', () => {
  const usagePath = path.join(USER_DATA, 'usage_proxy.json')
  if (!fs.existsSync(usagePath)) return []
  try {
    return fs.readFileSync(usagePath, 'utf-8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l))
  } catch { return [] }
})

// ============================================================
// Lifecycle
// ============================================================
app.whenReady().then(() => {
  createWindow()
  createTray()
  startProxy()
})
app.on('before-quit', () => {
  isQuitting = true
  stopProxy()
})
app.on('window-all-closed', () => {})
