const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  fetchBalance: () => ipcRenderer.invoke('fetch-balance'),
  fetchModels: () => ipcRenderer.invoke('fetch-models'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (c) => ipcRenderer.invoke('save-config', c),
  getBalanceHistory: () => ipcRenderer.invoke('get-balance-history'),
  getUsageData: () => ipcRenderer.invoke('get-usage-data'),
  ensureRefreshed: () => ipcRenderer.invoke('ensure-refreshed'),
  getProxyStatus: () => ipcRenderer.invoke('get-proxy-status'),
  getProxyUsage: () => ipcRenderer.invoke('get-proxy-usage'),
})
