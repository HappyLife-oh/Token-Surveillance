# Token Surveillance — 设计规格说明

> Windows 系统托盘 Token 用量监控工具 | 2026-05-08 | v1.0

## 项目目标

构建一个轻量级 Windows 系统托盘应用，监控 DeepSeek API 的账户余额和 Token 消耗。点击托盘图标弹出信息面板，展示余额、用量趋势和最近调用记录。

## 设计系统

### 视觉风格

- **风格**: 专业监控暗黑风 (Dark Mode OLED)
- **背景**: `#020617` (纯黑)
- **卡片**: `#0E1223`
- **强调绿**: `#059669` — 余额/正面指标/连接正常
- **警告琥珀**: `#D97706` — 用量异常标记
- **模型紫**: `#7C3AED` — 不同模型区分
- **前景文字**: `#F8FAFC` (主) / `#94A3B8` (次) / `#64748B` (三级)
- **边框**: `#1A1F2E` / `#334155`

### 字体

- **数字/代码/余额**: Fira Code (monospace) — 回退到 Consolas
- **正文/标签**: Fira Sans — 回退到 Segoe UI

### 间距

- 体系: 4pt 基础网格 (4, 8, 12, 16, 24)
- 面板内边距: 16px
- 卡片内边距: 12px
- 区块间距: 8-10px

## 架构

```
TokenSurveillance/
├── main.py                  # 入口: 托盘 + 面板初始化
├── src/
│   ├── __init__.py
│   ├── tray.py              # 系统托盘图标 + 菜单
│   ├── panel.py             # 弹出面板主窗口 (PyQt5 QWidget)
│   ├── api.py               # DeepSeek API 客户端
│   ├── models.py            # 数据模型 (dataclass)
│   ├── storage.py           # SQLite 历史数据存取
│   ├── charts.py            # pyqtgraph 柱状图组件
│   └── components/
│       ├── balance_card.py  # 余额卡片组件
│       ├── model_selector.py# 模型切换标签
│       └── call_history.py  # 最近调用列表
├── assets/
│   └── icon.ico             # 托盘图标
├── config.json              # 用户配置 (API Key 等)
└── requirements.txt
```

## 组件规格

### 1. 系统托盘 (tray.py)

- 图标: 16×16 / 32×32 .ico, 深色主题适配
- 右键菜单: "显示面板" / "立即刷新" / "设置" / "退出"
- 左键单击: 切换面板显示/隐藏
- 面板定位: 跟随托盘图标位置 (屏幕右下角附近弹出)

### 2. 弹出面板 (panel.py)

- 尺寸: 320×380px, 无边框, 置顶
- 失去焦点时自动隐藏
- 圆角 8px, 可选阴影

### 3. 余额卡片 (balance_card.py)

- 左侧 3px 绿色边框
- 大余额数字 (36px, Fira Code Bold)
- 子行: 今日用量 | 会话数 | 预估剩余天数
- 余额不足时 (< 阈值) 绿色 → 琥珀色/红色

### 4. 模型选择器 (model_selector.py)

- 从 `GET /v1/models` 动态获取模型列表
- 单行横向 tabs, 绿色边框指示当前选中
- 点击切换显示对应模型的用量

### 5. Token 柱状图 (charts.py)

- pyqtgraph BarGraphItem 实现
- 渐变质感: 底部透明绿 → 顶部实色 `#059669`
- 默认显示近 7 天, 可配置周期
- Hover tooltip: 精确 token 数 + 日期
- 最高柱(当日)使用琥珀色标记
- 坐标轴: 日期 (底部), 浅色网格线

### 6. 最近调用记录 (call_history.py)

- 最近 3 条调用记录的简化列表
- 每行: 模型名 | Token 数 | 相对时间
- Hover 高亮背景

## API 集成

### DeepSeek 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/user/balance` | GET | 查询账户余额 |
| `/v1/models` | GET | 获取可用模型列表 |

### 认证

- Header: `Authorization: Bearer <API_KEY>`
- API Key 存储在 `config.json` 中 (首次运行时弹窗输入)

### 余额响应格式

```json
{
  "is_available": true,
  "balance_infos": [{
    "currency": "CNY",
    "total_balance": "110.00",
    "granted_balance": "10.00",
    "topped_up_balance": "100.00"
  }]
}
```

### 模型列表响应格式

```json
{
  "data": [
    {"id": "deepseek-chat", "object": "model"},
    {"id": "deepseek-reasoner", "object": "model"}
  ]
}
```

## 数据存储 (storage.py)

- SQLite 数据库: `%APPDATA%/TokenSurveillance/usage.db`
- 表结构:
  ```sql
  CREATE TABLE usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    balance_after REAL
  );
  CREATE TABLE daily_summary (
    date TEXT PRIMARY KEY,
    total_tokens INTEGER,
    total_sessions INTEGER,
    model_name TEXT
  );
  ```

## 更新机制

1. **启动时**: 自动查询余额 + 模型列表
2. **弹出面板时**: 自动查询余额
3. **手动刷新**: 面板底部刷新按钮
4. **定时轮询**: 可配置间隔 (默认关闭, 建议 5-30min)

## 状态指示

| 状态 | 指示灯颜色 | 说明 |
|------|----------|------|
| 已连接 | 绿 `#22C55E` | API 正常响应 |
| 余额不足 | 琥珀 `#D97706` | 余额低于用户设置的阈值 |
| 断连/错误 | 红 `#EF4444` | API 请求失败 |

## 依赖

```
PyQt5>=5.15
pyqtgraph>=0.13
httpx>=0.27
```

## 验证方式

1. 启动应用 → 检查托盘图标出现
2. 点击图标 → 面板从托盘附近弹出
3. 面板显示余额 (从 DeepSeek API 获取)
4. 模型标签显示从 `/v1/models` 获取的列表
5. 柱状图渲染 7 天数据
6. 点击刷新 → 余额/用量更新
7. 失去焦点 → 面板自动隐藏
8. SQLite 历史数据正常写入和读取
