# Token Surveillance

Electron + Vue 3 桌面应用，Windows 系统托盘 Token 用量监控工具。监控 DeepSeek API 的账户余额和 Token 消耗。

## 项目目标

- 系统托盘常驻，点击弹出暗黑风格信息面板
- 实时显示 DeepSeek 余额、7日 Token 消耗柱状图、最近调用记录
- API Key 首次运行弹窗输入，持久化存储至 `%APPDATA%/TokenSurveillance/config.json`
- 单文件 exe 打包分发

## 文件结构

```
├── package.json               # 项目配置 + 依赖
├── vite.config.js             # Vite 构建配置
├── index.html                 # 入口 HTML
├── electron/
│   ├── main.js                # Electron 主进程（托盘 + 窗口 + IPC + API）
│   └── preload.js             # 安全 IPC bridge
├── src/                       # Vue 3 前端
│   ├── main.js                # Vue 入口
│   ├── App.vue                # 根组件（启动逻辑 / 设置/面板切换）
│   ├── stores/
│   │   └── app.js             # Pinia 状态管理
│   └── components/
│       ├── SetupDialog.vue    # API Key 输入弹窗
│       ├── PanelFrame.vue     # 面板框架（组装所有组件）
│       ├── BalanceCard.vue    # 余额卡片（大数字 + 今日用量）
│       ├── ModelSelector.vue  # 模型切换标签
│       ├── TokenChart.vue     # 7日柱状图 (ECharts)
│       └── CallHistory.vue    # 最近调用记录
├── assets/
│   └── icon.png               # 托盘图标
└── docs/superpowers/
    ├── specs/                 # 设计规格
    └── plans/                 # 实现计划
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面框架 | Electron 42 |
| 前端 | Vue 3 (Composition API) + Pinia |
| 构建 | Vite 8 |
| 图表 | ECharts 6 + vue-echarts |
| 打包 | electron-builder (portable exe) |

## 启动方式

```bash
npm run electron:dev    # 开发模式（热重载）
npm run build           # 仅构建前端
npm run electron:start  # 启动 Electron（需先 build）
npm run electron:build  # 打包为 exe
```

## 设计系统

- **风格**: 专业监控暗黑风 (Dark Mode OLED)
- **背景**: `#020617` / **卡片**: `#0E1223` / **边框**: `#1E293B`
- **强调绿**: `#059669` / **警告琥珀**: `#D97706` / **危险红**: `#EF4444`
- **数字字体**: Consolas, monospace

## API 端点

- `GET /user/balance` — 查询余额 (¥39.01)
- `GET /v1/models` — 获取模型列表 (deepseek-v4-flash, deepseek-v4-pro)
