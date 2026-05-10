# Token Surveillance — 项目规格书

> Windows 系统托盘 Token 用量监控工具 | v2.0 (Electron) | 2026-05-10

---

## 1. 项目定位

**一句话**：一款轻量、美观的 Windows 系统托盘工具，实时监控 AI API 账户余额和 Token 消耗。

**目标用户**：深度使用 DeepSeek / OpenAI 等 API 的开发者、Claude Code 用户。
**核心价值**：无需打开浏览器控制台，在系统托盘一目了然地查看 API 用量。
**设计理念**：打开即见、信息完整、暗黑专业、极低资源占用。

---

## 2. 技术栈

| 层级 | 技术 | 选择理由 |
|------|------|---------|
| **桌面框架** | Electron 33 | 跨平台 Windows 托盘原生支持，Node.js 已有 |
| **前端框架** | Vue 3 (Composition API) | 轻量响应式，上手快 |
| **构建工具** | Vite 6 | 秒级热重载，开发体验极佳 |
| **状态管理** | Pinia | Vue 3 官方推荐，比 Vuex 更轻 |
| **图表** | ECharts (vue-echarts) | 渐变柱状图、交互 tooltip、暗黑主题 |
| **样式** | Tailwind CSS | 快速构建专业 UI，暗黑主题天然适配 |
| **IPC** | contextBridge + ipcRenderer | 安全隔离主进程和渲染进程 |
| **打包** | electron-builder | 支持 portable exe 单文件分发 |

**架构图**：

```
┌─────────────────────────────────────────┐
│           Electron Main Process         │
│  ┌─────────┐  ┌──────────────────────┐  │
│  │  Tray   │  │  IPC Handlers        │  │
│  │  Icon   │  │  fetchBalance()      │  │
│  │  Menu   │  │  fetchModels()       │  │
│  │  Click  │──│  saveConfig()        │  │
│  └────┬────┘  └──────────┬───────────┘  │
│       │                  │              │
│  ┌────▼──────────────────▼───────────┐  │
│  │      BrowserWindow (frameless)    │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   Vue 3 Renderer Process   │  │  │
│  │  │   ┌───────┐ ┌───────────┐  │  │  │
│  │  │   │Pinia  │ │Components │  │  │  │
│  │  │   │Store  │◄┤(Vue SFC)  │  │  │  │
│  │  │   └───────┘ └───────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 3. 核心功能

### v1.0 功能清单

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 系统托盘常驻 | 托盘图标 (32x32)，左键弹出/隐藏面板 | P0 |
| 余额实时查询 | 调用 DeepSeek `/user/balance`，显示总余额/赠送金/充值金 | P0 |
| 模型列表同步 | 调用 `/v1/models`，动态获取可用模型并显示为切换标签 | P0 |
| 7日 Token 柱状图 | ECharts 渐变柱，hover 显示精确 token 数，最高柱琥珀高亮 | P0 |
| 最近调用记录 | 最近 3 条记录的模型名 + Token 数 + 相对时间 | P0 |
| API Key 管理 | 首次运行弹窗输入，本地持久化存储 | P0 |
| 面板可拖拽 | 无边框窗口，按住标题栏任意拖动 | P0 |
| 手动刷新 | 面板底部 Refresh 按钮 | P0 |
| 失去焦点自动隐藏 | 点击面板外部自动收起 | P0 |
| 状态指示灯 | 绿(已连接) / 红(错误/断连) | P0 |
| 余额阈值警告 | 余额 < ¥10 琥珀色，< ¥1 红色警告 | P1 |
| Tokens 今日用量 | 显示当日累计 token 消耗和会话数 | P1 |
| 预估可用天数 | 基于今日用量推算余额可持续天数 | P1 |
| 定时自动刷新 | 可配置间隔 (5/15/30min) | P1 |
| API 错误提示 | 连接失败时面板显示具体错误原因 | P1 |

### v2.0 (规划)

- 多 API 提供商支持 (OpenAI, Anthropic, Gemini)
- 调用记录手动录入（记录每次 LLM 调用的 token 消耗）
- 用量 CSV 导出
- 开机自启
- 全局快捷键 (Alt+T 呼出面板)
- 轻量 SQLite 历史趋势

---

## 4. UI 设计

### 设计系统

**风格**: 专业监控暗黑风 (Dark Mode OLED)
**尺寸**: 面板 340×420px，无边框圆角窗口

| Token | 色值 | 用途 |
|-------|------|------|
| 背景 | `#020617` | 面板背景 |
| 卡片 | `#0E1223` | 卡片/容器背景 |
| 强调绿 | `#059669` | 余额/正面指标/连接正常 |
| 警告琥珀 | `#D97706` | 用量异常/余额不足 |
| 危险红 | `#EF4444` | 错误/断连 |
| 主文字 | `#F1F5F9` | 标题/余额数字 |
| 次文字 | `#94A3B8` | 标签/模型名称 |
| 三级文字 | `#64748B` | 状态信息/时间 |
| 边框 | `#1E293B` | 容器边框/分割线 |
| 模型紫 | `#7C3AED` | 模型区分标识 |

**字体**:
- 数字/代码: `Consolas`, monospace
- 正文/标签: `Segoe UI`, system-ui

**间距体系**: 4pt 基准 (4, 8, 12, 16, 24)

### 布局 (自上而下)

```
┌──────────────────────────────────┐
│ ● TOKEN SURVEILLANCE     SYNC HH:mm│  ← 顶部状态栏 (可拖拽区)
├──────────────────────────────────┤
│ ┌────────────────────────────┐   │
│ │ BALANCE  [DeepSeek]        │   │  ← 余额卡片 (绿左边框)
│ │       ¥39.01               │   │    大数字 + 边框颜色随余额变化
│ │ Today 1.25M tok · 12 s. · ~38d│
│ └────────────────────────────┘   │
│                                  │
│ [deepseek-v4-flash] [deepseek-v4-pro] │  ← 模型切换标签
│                                  │
│ ┌────────────────────────────┐   │
│ │ 7-DAY TOKEN USAGE          │   │  ← ECharts 渐变柱状图
│ │ ┌──┬──┬──┬──┬──┬──┬──┐    │   │    hover tooltip
│ │ │  │  │  │  │  │  │  │    │   │    最高日琥珀色
│ │ └──┴──┴──┴──┴──┴──┴──┘    │   │
│ │ 05/01 05/03 05/05 05/07    │   │
│ └────────────────────────────┘   │
│                                  │
│ RECENT CALLS                     │
│ ┌────────────────────────────┐   │  ← 最近 3 条调用
│ │ deepseek-v4-flash  32.4k 3m│   │
│ │ deepseek-v4-pro    8.2k 12m│   │
│ │ deepseek-v4-flash  15.1k 28m│  │
│ └────────────────────────────┘   │
├──────────────────────────────────┤
│ DeepSeek API · Connected   ⟳ Refresh│  ← 底部状态栏
└──────────────────────────────────┘
```

### 交互规范

| 操作 | 行为 |
|------|------|
| 托盘左键单击 | 切换面板显示/隐藏 |
| 托盘右键 | 弹出菜单 (显示面板 / 退出) |
| 面板标题栏拖拽 | 按住任意位置拖动窗口 |
| 面板外部点击 | 自动隐藏面板 |
| Refresh 按钮 | 手动触发 API 刷新 |
| 模型标签点击 | 切换显示对应模型用量 |
| 柱状图 hover | Tooltip 显示精确 token 数 |

---

## 5. 数据处理流

```
[App Start]
     │
     ▼
[Load Config] ──→ 无 API Key? ──→ [SetupDialog: 输入 Key]
     │                                    │
     ▼                                    ▼
[Save Config] ◄──────────────────────────┘
     │
     ▼
[IPC: fetchBalance()] ────→ DeepSeek API ────→ [Pinia Store]
[IPC: fetchModels()]  ────→ DeepSeek API ────→ [Pinia Store]
     │
     ▼
[Vue Components Reactive Update]
```

---

## 6. 文件结构

```
TokenSurveillance/
├── package.json               # 项目配置 + 依赖
├── vite.config.js             # Vite 构建配置
├── index.html                 # 入口 HTML
├── electron/
│   ├── main.js                # Electron 主进程（托盘 + 窗口 + IPC）
│   └── preload.js             # 安全 IPC bridge
├── src/                       # Vue 3 前端
│   ├── main.js                # Vue 入口
│   ├── App.vue                # 根组件（路由/启动逻辑）
│   ├── stores/
│   │   └── app.js             # Pinia 状态管理
│   └── components/
│       ├── PanelFrame.vue     # 面板框架
│       ├── SetupDialog.vue    # API Key 输入
│       ├── BalanceCard.vue    # 余额卡片
│       ├── ModelSelector.vue  # 模型选择器
│       ├── TokenChart.vue     # 柱状图 (ECharts)
│       └── CallHistory.vue    # 最近调用
├── public/
│   └── icon.png               # 托盘图标
├── assets/
│   └── icon.png               # 源图标
└── docs/
    └── superpowers/
        ├── specs/             # 设计规格
        └── plans/             # 实现计划
```

---

## 7. 依赖清单

```json
{
  "dependencies": {
    "vue": "^3.5",
    "pinia": "^3.0",
    "echarts": "^5.6",
    "vue-echarts": "^7.0"
  },
  "devDependencies": {
    "electron": "^33.0",
    "vite": "^6.0",
    "@vitejs/plugin-vue": "^5.0",
    "electron-builder": "^25.0",
    "concurrently": "^9.0",
    "wait-on": "^8.0"
  }
}
```

---

## 8. 验证标准

1. `npm run electron:dev` 启动后托盘图标出现在系统托盘区
2. 首次运行弹出 API Key 输入对话框
3. 输入有效 Key 后面板自动弹出，显示余额和模型列表
4. 柱状图正常渲染，hover 显示 tooltip
5. 点击面板外部区域自动隐藏
6. 托盘右键 → 退出 → 进程完全终止
7. 再次启动时加载已保存的 Key，跳过设置对话框
8. `npm run electron:build` 生成单文件 exe
