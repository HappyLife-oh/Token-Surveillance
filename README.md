# Token Surveillance

Windows 系统托盘 DeepSeek API Token 用量监控工具。

## 功能

- **余额实时查询** — 调用 DeepSeek API 获取账户余额，自动保存历史快照
- **模型列表同步** — 从 API 获取可用模型列表并显示
- **Token 用量监控** — 通过本地代理中间层记录每一次 API 调用的 Token 消耗
- **CSV 数据导入** — 支持 DeepSeek 平台导出的用量 CSV
- **7日趋势图表** — ECharts 面积图/堆叠柱状图展示用量趋势
- **模型对比** — V4 Flash / V4 Pro 调用频率和资源消耗对比
- **本地代理** — 内嵌 HTTP 代理 (localhost:18999)，自动记录 Chat Completions 用量

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面框架 | Electron 42 |
| 前端 | Vue 3 (Composition API) + Pinia |
| 构建 | Vite 8 |
| 图表 | ECharts 6 |
| 图标 | SVG (Lucide 风格) |
| 字体 | Inter |

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 构建前端
npx vite build

# 3. 启动应用
npx electron .
```

首次启动会弹出 API Key 输入框，输入后在 `%APPDATA%/TokenSurveillance/` 持久化存储。

## 代理模式（实时 Token 监控）

应用启动后自动在 `localhost:18999` 启动 HTTP 代理。将 Claude Code / 其他客户端的 API 地址改为：

```
http://localhost:18999
```

所有请求的 Token 消耗自动记录到 `%APPDATA%/TokenSurveillance/usage_proxy.json`，面板实时显示。

## 开发

```bash
npm run dev            # Vite 开发服务器
npm run electron:dev   # Vite + Electron 热重载
npm run electron:build # 打包 Windows exe
```

## GitHub Actions

每次 push 自动触发 electron-builder 构建 Windows 可执行文件，产物在 Actions 页面下载。

## 数据来源

| 数据 | 来源 |
|------|------|
| 余额 | DeepSeek API (`GET /user/balance`) |
| 模型列表 | DeepSeek API (`GET /v1/models`) |
| Token 用量 | 本地代理记录 / CSV 导出导入 |
| 历史趋势 | 本地 balance_history.json |
