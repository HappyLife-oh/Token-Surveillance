# Proxy + CI/CD 实现计划

**Goal:** 本地代理记录 Token 用量 + 推送到 GitHub + Actions 自动构建

**Tasks:** 1-proxy-server 2-main.js集成 3-拖拽修复 4-Git初始化 5-GitHub Actions 6-验证

---

### Task 1: proxy-server.js

- [ ] 创建 `electron/proxy-server.js`，纯 Node.js HTTP 代理

### Task 2: main.js 集成代理

- [ ] 修改 `electron/main.js` 添加子进程管理
- [ ] 修改 `electron/preload.js` 添加代理状态 IPC

### Task 3: 拖拽修复

- [ ] 修改 `src/App.vue`，`-webkit-app-region: drag` 移到 `.dashboard`，交互元素加 `no-drag`

### Task 4: Git 初始化 + GitHub

- [ ] `git init` → commit → remote add → push

### Task 5: GitHub Actions

- [ ] 创建 `.github/workflows/build.yml`，electron-builder 构建 Windows exe

### Task 6: 集成验证

- [ ] 启动 Electron → 代理运行 → 面板可拖拽 → 完整测试
