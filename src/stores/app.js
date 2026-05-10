import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const balance = ref(null)
  const models = ref([])
  const error = ref('')
  const syncTime = ref('')
  const balanceHistory = ref([])
  const usageData = ref([])
  const selectedModel = ref(null) // null=All, or model id string

  // --- Balance ---
  const balanceInfo = computed(() => balance.value?.balance_infos?.[0] || null)
  const totalBalance = computed(() => parseFloat(balanceInfo.value?.total_balance || 0))
  const grantedBalance = computed(() => parseFloat(balanceInfo.value?.granted_balance || 0))
  const toppedUpBalance = computed(() => parseFloat(balanceInfo.value?.topped_up_balance || 0))
  const isAvailable = computed(() => balance.value?.is_available ?? false)

  // --- Model filter options ---
  const modelOptions = computed(() => {
    const set = new Set(usageData.value.map((d) => d.model))
    return ['all', ...Array.from(set)]
  })

  const filteredData = computed(() => {
    if (!selectedModel.value || selectedModel.value === 'all') return usageData.value
    return usageData.value.filter((d) => d.model === selectedModel.value)
  })

  // --- Monthly spending from CSV cost data ---
  const dailyCosts = computed(() => {
    const map = {}
    filteredData.value.forEach((d) => {
      if (d.cost) {
        if (!map[d.date]) map[d.date] = { date: d.date, total: 0 }
        map[d.date].total += d.cost
      }
    })
    return Object.values(map).sort((a, b) => a.date.localeCompare(b.date))
  })

  const monthlySpending = computed(() => {
    if (!dailyCosts.value.length) return null
    return parseFloat(dailyCosts.value.reduce((s, d) => s + d.total, 0).toFixed(2))
  })

  // --- Model breakdown ---
  const modelBreakdown = computed(() => {
    const byModel = {}
    usageData.value.forEach((d) => {
      if (!byModel[d.model]) byModel[d.model] = { model: d.model, requests: 0, cached: 0, uncached: 0, output: 0, cost: 0 }
      byModel[d.model].requests += d.requests || 0
      byModel[d.model].cached += d.cached || 0
      byModel[d.model].uncached += d.uncached || 0
      byModel[d.model].output += d.output || 0
      byModel[d.model].cost += d.cost || 0
    })
    return Object.values(byModel).map((m) => ({
      id: m.model,
      label: m.model.replace('deepseek-', '').replace('v4-', 'V4 '),
      count: m.requests,
      tokens: m.cached + m.uncached + m.output,
      cost: parseFloat(m.cost.toFixed(2)),
      cached: m.cached, uncached: m.uncached, output: m.output,
      color: m.model.includes('flash') ? '#3B82F6' : '#8B5CF6',
      glow: m.model.includes('flash') ? 'rgba(59,130,246,0.3)' : 'rgba(139,92,246,0.3)',
    }))
  })

  const totalTokensAll = computed(() => modelBreakdown.value.reduce((s, m) => s + m.tokens, 0))
  const totalCalls = computed(() => modelBreakdown.value.reduce((s, m) => s + m.count, 0))

  // --- Helper: fill missing dates ---
  function fillDateRange(data, dateField, startStr, endStr) {
    const start = new Date(startStr)
    const end = new Date(endStr)
    const map = {}
    data.forEach((d) => { map[d[dateField]] = d })
    const result = []
    const d = new Date(start)
    while (d <= end) {
      const key = d.toISOString().slice(0, 10)
      if (map[key]) { result.push(map[key]) } else {
        const blank = { [dateField]: key }
        if (data.length) Object.keys(data[0]).forEach((k) => { if (k !== dateField) blank[k] = 0 })
        result.push(blank)
      }
      d.setDate(d.getDate() + 1)
    }
    return result
  }
  const DATA_START = '2026-05-01'
  const DATA_END = new Date().toISOString().slice(0, 10)

  // --- Daily request frequency (for area chart) ---
  const dailyRequests = computed(() => {
    const map = {}
    filteredData.value.forEach((d) => {
      if (!map[d.date]) map[d.date] = { date: d.date, flash: 0, pro: 0, total: 0 }
      map[d.date].total += d.requests || 0
      if (d.model?.includes('flash')) map[d.date].flash += d.requests || 0
      else map[d.date].pro += d.requests || 0
    })
    return fillDateRange(Object.values(map), 'date', DATA_START, DATA_END)
  })

  // --- Daily token composition (stacked bar, filtered by selected model) ---
  const dailyTokenComposition = computed(() => {
    const map = {}
    filteredData.value.forEach((d) => {
      if (!map[d.date]) map[d.date] = { date: d.date, cached: 0, uncached: 0, output: 0 }
      map[d.date].cached += d.cached || 0
      map[d.date].uncached += d.uncached || 0
      map[d.date].output += d.output || 0
    })
    return fillDateRange(Object.values(map), 'date', DATA_START, DATA_END)
  })

  // --- Balance trend ---
  const balanceTrend = computed(() => {
    const last7 = balanceHistory.value.slice(-7)
    return last7.map((s) => ({ date: s.time.slice(0, 10), balance: s.total }))
  })

  const sparklineData = computed(() => balanceHistory.value.slice(-7).map((s) => Math.round(s.total * 100)))

  // --- Actions ---
  async function refresh() {
    const [balResult, modResult] = await Promise.all([
      window.electronAPI.fetchBalance(),
      window.electronAPI.fetchModels(),
    ])
    if (balResult.data) {
      balance.value = balResult.data
      error.value = ''
    } else {
      error.value = balResult.error || 'API Error'
      balance.value = null
    }
    if (modResult.data?.data) models.value = modResult.data.data

    balanceHistory.value = (await window.electronAPI.getBalanceHistory()) || []
    usageData.value = (await window.electronAPI.getUsageData()) || []

    syncTime.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return {
    balance, models, error, syncTime,
    balanceInfo, totalBalance, grantedBalance, toppedUpBalance, isAvailable,
    monthlySpending, dailyCosts, modelBreakdown, totalTokensAll, totalCalls,
    dailyRequests, dailyTokenComposition, balanceTrend, sparklineData,
    selectedModel, modelOptions,
    refresh,
  }
})
