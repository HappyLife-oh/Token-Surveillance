# Token Surveillance — 代理中间层 + CI/CD 集成规格

> 2026-05-10 | v2.1

---

## 1. 架构总览

```
┌─────────────────────────────────────────────────────┐
│                  用户桌面环境                         │
│                                                      │
│  ┌──────────────┐      ┌────────────────────────┐   │
│  │ Claude Code  │─────▶│  本地代理 (localhost)   │   │
│  │              │      │  :18999                 │   │
│  │ API 地址改为  │      │          │              │   │
│  │ localhost:18999     │    转发到 api.deepseek.com │  │
│  └──────────────┘      └──────┬─────────────────┘   │
│                               │                      │
│                       记录 usage 到                  │
│                    usage_proxy.json                  │
│                               │                      │
│  ┌────────────────────────────┴──────────────────┐   │
│  │        Electron 面板 (读取 usage_proxy.json)     │   │
│  │  ├ 代理子进程管理 (启动/停止/状态)               │   │
│  │  └ 实时显示代理记录的用量                        │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 2. 代理中间层 (Proxy Server)

### 技术实现

- 纯 Node.js `http` 模块，无外部依赖
- Electron 启动时通过 `child_process.fork()` 启动代理
- 监听 `localhost:18999`
- 拦截 `/v1/chat/completions` 请求
- 转发到 `api.deepseek.com`，同时 clone 响应流
- 从响应 JSON 中提取 `usage` 字段 (prompt_tokens, completion_tokens, total_tokens)
- 追加写入 `%APPDATA%/TokenSurveillance/usage_proxy.json`

### 关键代码结构

```
electron/
├── main.js           # + 代理生命周期管理
├── proxy-server.js   # HTTP 代理服务器
└── preload.js        # + 代理状态 IPC
```

### proxy-server.js 核心逻辑

```javascript
const http = require('http')
const https = require('https')
const fs = require('fs')
const path = require('path')

// 1. 接收客户端请求
// 2. 转发到 api.deepseek.com
// 3. 收集响应 body
// 4. 解析 usage 字段
// 5. 写入日志文件
// 6. 响应返回给客户端
```

### 数据格式

```json
// usage_proxy.json — 追加写入，每行一个 JSON
{"time":"2026-05-10T20:30:00Z","model":"deepseek-v4-flash","prompt_tokens":452,"completion_tokens":1280,"total_tokens":1732,"cached":310}
```

## 3. 面板拖拽修复

### 问题
当前 `-webkit-app-region: drag` 在 header 上，但面板背景透明导致点击区域不命中。

### 修复方案
- 将 `-webkit-app-region: drag` 设在 `.dashboard` 容器（整个面板背景）
- 所有可交互元素（按钮、图表）加 `-webkit-app-region: no-drag`
- 这样用户可以在面板任意空白区域拖拽

## 4. GitHub 仓库 + Actions

### 仓库设置

```bash
cd "E:\SparkHub\Token Surveillance"
git init
git add .
git commit -m "feat: initial Electron + Vue 3 Token Surveillance"
git remote add origin https://github.com/HappyLife-oh/Token-Surveillance.git
git push -u origin main
```

### GitHub Actions (electron-builder)

```yaml
# .github/workflows/build.yml
name: Build Windows
on: push
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx vite build
      - run: npx electron-builder --win portable
      - uses: actions/upload-artifact@v4
        with:
          name: Token-Surveillance
          path: release/*.exe
```

## 5. 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `electron/proxy-server.js` | 新建 | HTTP 代理服务器 |
| `electron/main.js` | 修改 | + 代理子进程管理 |
| `electron/preload.js` | 修改 | + 代理状态 IPC |
| `src/stores/app.js` | 修改 | + 代理数据源 |
| `src/components/MonitorPanel.vue` | 修改 | + 代理状态指示 |
| `.github/workflows/build.yml` | 新建 | GitHub Actions |
| `src/App.vue` | 修改 | 拖拽区域修复 |

## 6. 验证标准

1. 启动 Electron → 代理自动在 :18999 启动
2. `curl http://localhost:18999/v1/chat/completions ...` 正常转发并记录
3. 面板显示代理记录的实时用量
4. 面板任意空白区域可拖拽
5. `git push` 触发 GitHub Actions 构建
6. Actions artifact 产出 `.exe` 可下载
