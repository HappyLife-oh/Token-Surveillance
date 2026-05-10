# Token Surveillance 实现计划

> **For agentic workers:** 使用 `subagent-driven-development` 或 `executing-plans` 按任务执行。步骤使用 checkbox (`- [ ]`) 语法跟踪进度。

**目标:** 构建 Windows 系统托盘应用，监控 DeepSeek API 余额和 Token 消耗，弹出信息面板展示用量图表。

**架构:** Python + PyQt5 托盘 + 弹出面板，httpx 同步 API 调用在 QThread 中运行。SQLite 存储历史数据，pyqtgraph 渲染柱状图。

**技术栈:** Python 3.12, PyQt5, pyqtgraph, httpx, sqlite3

---

### Task 1: 项目脚手架

**文件:**
- 创建: `requirements.txt`
- 创建: `src/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
PyQt5>=5.15
pyqtgraph>=0.13
httpx>=0.27
```

- [ ] **Step 2: 创建 src/__init__.py**

空文件。

- [ ] **Step 3: 创建目录结构**

```bash
mkdir -p "E:\SparkHub\Token Surveillance\src\components" "E:\SparkHub\Token Surveillance\assets"
```

- [ ] **Step 4: 安装依赖**

```bash
pip install -r requirements.txt
```

---

### Task 2: 数据模型

**文件:**
- 创建: `src/models.py`
- 创建: `tests/test_models.py`

- [ ] **Step 1: 编写数据模型测试**

```python
# tests/test_models.py
import sys
sys.path.insert(0, "src")

from models import Balance, BalanceInfo, ModelInfo, UsageLog, DailySummary


def test_balance_info_from_dict():
    data = {"currency": "CNY", "total_balance": "110.00", "granted_balance": "10.00", "topped_up_balance": "100.00"}
    bi = BalanceInfo.from_dict(data)
    assert bi.currency == "CNY"
    assert bi.total_balance == 110.00
    assert bi.granted_balance == 10.00
    assert bi.topped_up_balance == 100.00


def test_balance_from_response():
    response = {
        "is_available": True,
        "balance_infos": [{"currency": "CNY", "total_balance": "50.00", "granted_balance": "0.00", "topped_up_balance": "50.00"}]
    }
    b = Balance.from_response(response)
    assert b.is_available is True
    assert len(b.balance_infos) == 1
    assert b.balance_infos[0].total_balance == 50.00


def test_model_info_from_dict():
    data = {"id": "deepseek-chat", "object": "model"}
    m = ModelInfo.from_dict(data)
    assert m.id == "deepseek-chat"
    assert m.object == "model"


def test_usage_log_creation():
    log = UsageLog(model_name="deepseek-chat", token_count=32400, balance_after=47.32)
    assert log.model_name == "deepseek-chat"
    assert log.token_count == 32400
    assert log.balance_after == 47.32


def test_daily_summary_creation():
    ds = DailySummary(date="2026-05-08", total_tokens=1245800, total_sessions=12, model_name="deepseek-chat")
    assert ds.total_tokens == 1245800
    assert ds.total_sessions == 12
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_models.py -v
```
预期: 全部 FAIL (模块不存在)

- [ ] **Step 3: 实现数据模型**

```python
# src/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BalanceInfo:
    currency: str
    total_balance: float
    granted_balance: float
    topped_up_balance: float

    @classmethod
    def from_dict(cls, d: dict) -> "BalanceInfo":
        return cls(
            currency=d["currency"],
            total_balance=float(d["total_balance"]),
            granted_balance=float(d["granted_balance"]),
            topped_up_balance=float(d["topped_up_balance"]),
        )


@dataclass
class Balance:
    is_available: bool
    balance_infos: list[BalanceInfo] = field(default_factory=list)

    @classmethod
    def from_response(cls, data: dict) -> "Balance":
        return cls(
            is_available=data["is_available"],
            balance_infos=[BalanceInfo.from_dict(bi) for bi in data.get("balance_infos", [])],
        )


@dataclass
class ModelInfo:
    id: str
    object: str

    @classmethod
    def from_dict(cls, d: dict) -> "ModelInfo":
        return cls(id=d["id"], object=d.get("object", ""))


@dataclass
class UsageLog:
    model_name: str
    token_count: int
    balance_after: float
    id: Optional[int] = None
    timestamp: Optional[datetime] = None


@dataclass
class DailySummary:
    date: str
    total_tokens: int
    total_sessions: int
    model_name: str = ""
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_models.py -v
```
预期: 5 passed

---

### Task 3: 配置管理

**文件:**
- 创建: `src/config.py`
- 创建: `tests/test_config.py`

- [ ] **Step 1: 编写配置测试**

```python
# tests/test_config.py
import json
import tempfile
import os
import sys
sys.path.insert(0, "src")

from config import AppConfig


def test_default_config():
    cfg = AppConfig.default()
    assert cfg.api_key == ""
    assert cfg.balance_threshold == 10.0
    assert cfg.auto_refresh_minutes == 0


def test_save_and_load():
    cfg = AppConfig(api_key="sk-test-123", balance_threshold=5.0, auto_refresh_minutes=10)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        cfg.save(f.name)
        path = f.name
    try:
        loaded = AppConfig.load(path)
        assert loaded.api_key == "sk-test-123"
        assert loaded.balance_threshold == 5.0
        assert loaded.auto_refresh_minutes == 10
    finally:
        os.unlink(path)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_config.py -v
```
预期: FAIL (模块不存在)

- [ ] **Step 3: 实现配置管理**

```python
# src/config.py
import json
import os
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    api_key: str = ""
    balance_threshold: float = 10.0
    auto_refresh_minutes: int = 0

    @classmethod
    def default(cls) -> "AppConfig":
        return cls()

    @classmethod
    def load(cls, path: str) -> "AppConfig":
        if not os.path.exists(path):
            return cls.default()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            api_key=data.get("api_key", ""),
            balance_threshold=data.get("balance_threshold", 10.0),
            auto_refresh_minutes=data.get("auto_refresh_minutes", 0),
        )

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_config.py -v
```
预期: 2 passed

---

### Task 4: DeepSeek API 客户端

**文件:**
- 创建: `src/api.py`
- 创建: `tests/test_api.py`

- [ ] **Step 1: 编写 API 客户端测试**

```python
# tests/test_api.py
import sys
sys.path.insert(0, "src")

from unittest.mock import patch, MagicMock
from api import DeepSeekClient
from models import Balance, BalanceInfo, ModelInfo
from config import AppConfig


def test_get_balance_success():
    config = AppConfig(api_key="sk-test")
    client = DeepSeekClient(config)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "is_available": True,
        "balance_infos": [{"currency": "CNY", "total_balance": "110.00", "granted_balance": "10.00", "topped_up_balance": "100.00"}]
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client._client, "get", return_value=mock_response) as mock_get:
        result = client.get_balance()
        mock_get.assert_called_once_with("https://api.deepseek.com/user/balance")
        assert result.is_available is True
        assert result.balance_infos[0].total_balance == 110.00


def test_get_balance_unauthorized():
    import httpx
    config = AppConfig(api_key="sk-invalid")
    client = DeepSeekClient(config)

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
    )

    with patch.object(client._client, "get", return_value=mock_response):
        result = client.get_balance()
        assert result is None
        assert client.last_error == "API 认证失败，请检查 API Key"


def test_get_models_success():
    config = AppConfig(api_key="sk-test")
    client = DeepSeekClient(config)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"id": "deepseek-chat", "object": "model"}, {"id": "deepseek-reasoner", "object": "model"}]
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client._client, "get", return_value=mock_response) as mock_get:
        result = client.get_models()
        mock_get.assert_called_once_with("https://api.deepseek.com/v1/models")
        assert len(result) == 2
        assert result[0].id == "deepseek-chat"


def test_fetch_all_success():
    config = AppConfig(api_key="sk-test")
    client = DeepSeekClient(config)

    mock_balance_resp = MagicMock()
    mock_balance_resp.json.return_value = {
        "is_available": True,
        "balance_infos": [{"currency": "CNY", "total_balance": "50.00", "granted_balance": "0.00", "topped_up_balance": "50.00"}]
    }
    mock_balance_resp.raise_for_status.return_value = None

    mock_models_resp = MagicMock()
    mock_models_resp.json.return_value = {
        "data": [{"id": "deepseek-chat", "object": "model"}]
    }
    mock_models_resp.raise_for_status.return_value = None

    with patch.object(client._client, "get", side_effect=[mock_balance_resp, mock_models_resp]):
        balance, models = client.fetch_all()
        assert balance is not None
        assert balance.balance_infos[0].total_balance == 50.00
        assert len(models) == 1
        assert models[0].id == "deepseek-chat"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_api.py -v
```
预期: FAIL (模块不存在)

- [ ] **Step 3: 实现 API 客户端**

```python
# src/api.py
import httpx
from config import AppConfig
from models import Balance, ModelInfo


class DeepSeekClient:
    BASE_URL = "https://api.deepseek.com"

    def __init__(self, config: AppConfig):
        self.config = config
        self.last_error: str = ""
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Accept": "application/json",
            },
            timeout=10.0,
        )

    def get_balance(self) -> Balance | None:
        try:
            resp = self._client.get("/user/balance")
            resp.raise_for_status()
            self.last_error = ""
            return Balance.from_response(resp.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.last_error = "API 认证失败，请检查 API Key"
            else:
                self.last_error = f"API 请求失败: HTTP {e.response.status_code}"
            return None
        except httpx.RequestError as e:
            self.last_error = f"网络连接失败: {e}"
            return None

    def get_models(self) -> list[ModelInfo]:
        try:
            resp = self._client.get("/v1/models")
            resp.raise_for_status()
            self.last_error = ""
            data = resp.json()
            return [ModelInfo.from_dict(m) for m in data.get("data", [])]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.last_error = "API 认证失败，请检查 API Key"
            else:
                self.last_error = f"获取模型列表失败: HTTP {e.response.status_code}"
            return []
        except httpx.RequestError as e:
            self.last_error = f"网络连接失败: {e}"
            return []

    def fetch_all(self) -> tuple[Balance | None, list[ModelInfo]]:
        return self.get_balance(), self.get_models()

    def close(self):
        self._client.close()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_api.py -v
```
预期: 4 passed

---

### Task 5: SQLite 存储

**文件:**
- 创建: `src/storage.py`
- 创建: `tests/test_storage.py`

- [ ] **Step 1: 编写存储测试**

```python
# tests/test_storage.py
import os
import tempfile
import sys
sys.path.insert(0, "src")

from storage import Storage
from models import UsageLog, DailySummary


def test_insert_and_query_usage():
    db_path = tempfile.mktemp(suffix=".db")
    try:
        s = Storage(db_path)
        s.insert_usage("deepseek-chat", 32400, 47.32)
        s.insert_usage("deepseek-reasoner", 8200, 47.30)

        logs = s.get_recent_calls(limit=5)
        assert len(logs) == 2
        assert logs[0].model_name == "deepseek-reasoner"  # most recent first
        assert logs[0].token_count == 8200
    finally:
        os.unlink(db_path)


def test_daily_summary():
    db_path = tempfile.mktemp(suffix=".db")
    try:
        s = Storage(db_path)
        s.upsert_daily_summary("2026-05-08", 500000, 5, "deepseek-chat")
        s.upsert_daily_summary("2026-05-08", 700000, 8, "deepseek-chat")

        data = s.get_weekly_summary(7)
        assert len(data) == 1
        assert data[0].total_tokens == 700000
        assert data[0].total_sessions == 8
    finally:
        os.unlink(db_path)


def test_weekly_summary_empty():
    db_path = tempfile.mktemp(suffix=".db")
    try:
        s = Storage(db_path)
        data = s.get_weekly_summary(7)
        assert data == []
    finally:
        os.unlink(db_path)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_storage.py -v
```

- [ ] **Step 3: 实现存储层**

```python
# src/storage.py
import sqlite3
import os
from models import UsageLog, DailySummary


class Storage:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_name TEXT NOT NULL,
                token_count INTEGER NOT NULL,
                balance_after REAL
            );
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT NOT NULL,
                total_tokens INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                model_name TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (date, model_name)
            );
        """)
        self.conn.commit()

    def insert_usage(self, model_name: str, token_count: int, balance_after: float):
        self.conn.execute(
            "INSERT INTO usage_log (model_name, token_count, balance_after) VALUES (?, ?, ?)",
            (model_name, token_count, balance_after),
        )
        self.conn.commit()

    def get_recent_calls(self, limit: int = 3) -> list[UsageLog]:
        rows = self.conn.execute(
            "SELECT id, timestamp, model_name, token_count, balance_after "
            "FROM usage_log ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [UsageLog(
            id=r["id"], timestamp=r["timestamp"], model_name=r["model_name"],
            token_count=r["token_count"], balance_after=r["balance_after"],
        ) for r in rows]

    def upsert_daily_summary(self, date: str, tokens: int, sessions: int, model_name: str = ""):
        self.conn.execute("""
            INSERT INTO daily_summary (date, total_tokens, total_sessions, model_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date, model_name) DO UPDATE SET
                total_tokens = excluded.total_tokens,
                total_sessions = excluded.total_sessions
        """, (date, tokens, sessions, model_name))
        self.conn.commit()

    def get_weekly_summary(self, days: int = 7) -> list[DailySummary]:
        rows = self.conn.execute("""
            SELECT date, SUM(total_tokens) as total_tokens, SUM(total_sessions) as total_sessions
            FROM daily_summary
            WHERE date >= date('now', ? || ' days')
            GROUP BY date ORDER BY date ASC
        """, (f"-{days}",)).fetchall()
        return [DailySummary(
            date=r["date"], total_tokens=r["total_tokens"],
            total_sessions=r["total_sessions"],
        ) for r in rows]

    def close(self):
        self.conn.close()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_storage.py -v
```
预期: 3 passed

---

### Task 6: API 工作线程

**文件:**
- 创建: `src/worker.py`

- [ ] **Step 1: 实现后台 API 查询线程**

```python
# src/worker.py
from PyQt5.QtCore import QThread, pyqtSignal
from api import DeepSeekClient
from models import Balance, ModelInfo


class RefreshWorker(QThread):
    finished = pyqtSignal(object, object, str)  # balance, models, error

    def __init__(self, client: DeepSeekClient, parent=None):
        super().__init__(parent)
        self.client = client

    def run(self):
        try:
            balance = self.client.get_balance()
            models = self.client.get_models()
            self.finished.emit(balance, models, self.client.last_error)
        except Exception as e:
            self.finished.emit(None, [], str(e))
```

---

### Task 7: 系统托盘

**文件:**
- 创建: `src/tray.py`

- [ ] **Step 1: 生成托盘图标**

使用 Python 代码生成一个 16×16 的 tray 图标（绿色 S 字母 + 黑背景）：

```python
# scripts/generate_icon.py
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys

app = QApplication(sys.argv)
from PyQt5.QtGui import QPixmap, QIcon

size = 32
pixmap = QPixmap(size, size)
pixmap.fill(QColor("#020617"))

painter = QPainter(pixmap)
painter.setRenderHint(QPainter.Antialiasing)
painter.setPen(QColor("#22C55E"))
painter.setBrush(QColor("#22C55E"))
painter.drawEllipse(2, 2, size - 4, size - 4)

painter.setPen(QColor("#020617"))
font = QFont("Segoe UI", 16, QFont.Bold)
painter.setFont(font)
painter.drawText(pixmap.rect(), Qt.AlignCenter, "S")

painter.end()
pixmap.save("assets/icon.png")
print("Icon generated: assets/icon.png")
```

运行: `python scripts/generate_icon.py`

- [ ] **Step 2: 实现系统托盘**

```python
# src/tray.py
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal


class TrayController(QObject):
    refresh_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    panel_toggle_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon(parent)
        self.tray.setToolTip("Token Surveillance")

        icon = self._load_icon()
        self.tray.setIcon(icon)

        menu = QMenu()
        self._show_action = menu.addAction("显示面板")
        self._show_action.triggered.connect(self.panel_toggle_requested.emit)

        self._refresh_action = menu.addAction("立即刷新")
        self._refresh_action.triggered.connect(self.refresh_requested.emit)

        menu.addSeparator()

        self._settings_action = menu.addAction("设置...")
        self._settings_action.triggered.connect(self.settings_requested.emit)

        self._quit_action = menu.addAction("退出")
        self._quit_action.triggered.connect(QSystemTrayIcon.parent)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)

    def _load_icon(self) -> QIcon:
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        # 回退: 纯绿色方块
        from PyQt5.QtGui import QPixmap, QColor
        pix = QPixmap(32, 32)
        pix.fill(QColor("#22C55E"))
        return QIcon(pix)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.panel_toggle_requested.emit()

    def set_status_ok(self):
        self.tray.setToolTip("Token Surveillance - Connected")

    def set_status_error(self, msg: str = ""):
        self.tray.setToolTip(f"Token Surveillance - {msg}" if msg else "Token Surveillance - Disconnected")

    def show(self):
        self.tray.show()

    def set_visible(self, v: bool):
        self.tray.setVisible(v)
```

---

### Task 8: 余额卡片组件

**文件:**
- 创建: `src/components/__init__.py`
- 创建: `src/components/balance_card.py`

- [ ] **Step 1: 实现余额卡片**

```python
# src/components/balance_card.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from models import Balance


class BalanceCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            BalanceCard {
                background: #0E1223;
                border-left: 3px solid #059669;
                border-radius: 6px;
                padding: 12px 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self._label_title = QLabel("BALANCE · DeepSeek")
        self._label_title.setStyleSheet("color: #64748B; font-size: 9px; letter-spacing: 1px; border: none;")

        self._balance_amount = QLabel("--")
        self._balance_amount.setStyleSheet(
            "color: #F0F0F0; font-size: 38px; font-weight: 800; "
            "font-family: 'Fira Code', 'Consolas', monospace; border: none;"
        )

        self._info_row = QLabel("Today -- tok · -- sessions · Est. --d")
        self._info_row.setStyleSheet("color: #64748B; font-size: 10px; border: none;")

        layout.addWidget(self._label_title)
        layout.addWidget(self._balance_amount)
        layout.addWidget(self._info_row)

    def update_balance(self, balance: Balance):
        bi = balance.balance_infos[0] if balance.balance_infos else None
        if bi:
            self._balance_amount.setText(f"¥{bi.total_balance:.2f}")
            self._label_title.setText(f"BALANCE · DeepSeek ({bi.currency})")
            if bi.total_balance < 10.0:
                self.setStyleSheet(self.styleSheet().replace("#059669", "#D97706"))
            elif bi.total_balance < 1.0:
                self.setStyleSheet(self.styleSheet().replace("#059669", "#EF4444"))
            else:
                self.setStyleSheet(self.styleSheet().replace("#D97706", "#059669").replace("#EF4444", "#059669"))

    def update_daily_usage(self, tokens_today: int, sessions_today: int, estimated_days: int):
        tokens_str = f"{tokens_today / 1e6:.2f}M" if tokens_today >= 1e6 else f"{tokens_today:,}"
        self._info_row.setText(
            f"Today {tokens_str} tok · {sessions_today} sessions · Est. ~{estimated_days}d"
        )

    def clear(self):
        self._balance_amount.setText("--")
        self._info_row.setText("Today -- tok · -- sessions · Est. --d")
```

---

### Task 9: 模型选择器组件

**文件:**
- 创建: `src/components/model_selector.py`

- [ ] **Step 1: 实现模型选择器**

```python
# src/components/model_selector.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from models import ModelInfo


class ModelSelector(QWidget):
    model_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        self._model_ids: list[str] = []
        self._selected: str = ""

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

    def set_models(self, models: list[ModelInfo]):
        for btn in self._buttons:
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()
        self._model_ids = []

        for m in models:
            btn = QPushButton(m.id)
            btn.setCheckable(True)
            btn.setStyleSheet(self._btn_style(False))
            btn.clicked.connect(lambda checked, mid=m.id: self._on_click(mid))
            self._layout.addWidget(btn)
            self._buttons.append(btn)
            self._model_ids.append(m.id)

        if self._model_ids:
            self._select(self._model_ids[0])

    def _btn_style(self, selected: bool) -> str:
        border = "#059669" if selected else "transparent"
        opacity = "1.0" if selected else "0.6"
        return f"""
            QPushButton {{
                background: #0E1223; color: #94A3B8; border: 1px solid {border};
                border-radius: 5px; padding: 6px 10px; font-size: 10px;
                font-family: 'Fira Code', monospace; opacity: {opacity};
            }}
            QPushButton:hover {{ border-color: #059669; }}
        """

    def _select(self, model_id: str):
        self._selected = model_id
        for i, mid in enumerate(self._model_ids):
            self._buttons[i].setStyleSheet(self._btn_style(mid == model_id))
            self._buttons[i].setChecked(mid == model_id)
        self.model_changed.emit(model_id)

    def _on_click(self, model_id: str):
        self._select(model_id)

    def current_model(self) -> str:
        return self._selected
```

---

### Task 10: Token 柱状图组件

**文件:**
- 创建: `src/charts.py`

- [ ] **Step 1: 实现 pyqtgraph 柱状图**

```python
# src/charts.py
import pyqtgraph as pg
from pyqtgraph import BarGraphItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from models import DailySummary
from datetime import datetime, timedelta


class TokenChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.setStyleSheet("background: #0E1223; border-radius: 6px;")

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)

        title = QLabel("7-DAY TOKEN USAGE")
        title.setStyleSheet("color: #64748B; font-size: 9px; letter-spacing: 1px; border: none; background: transparent;")
        self._delta = QLabel("")
        self._delta.setStyleSheet("color: #D97706; font-size: 9px; font-family: 'Fira Code', monospace; border: none; background: transparent;")
        header_layout.addWidget(title)
        header_layout.addWidget(self._delta)

        layout.addWidget(header)

        self._pw = pg.PlotWidget()
        self._pw.setBackground("#0E1223")
        self._pw.showGrid(x=False, y=True, alpha=0.1)
        self._pw.getAxis("left").setPen(pg.mkPen("#334155"))
        self._pw.getAxis("left").setTextPen(pg.mkPen("#64748B"))
        self._pw.getAxis("bottom").setPen(pg.mkPen("#334155"))
        self._pw.getAxis("bottom").setTextPen(pg.mkPen("#64748B"))
        self._pw.setMinimumHeight(90)
        self._pw.setMaximumHeight(120)
        self._pw.hideButtons()
        self._pw.setMouseEnabled(x=False, y=False)

        layout.addWidget(self._pw)

    def update_data(self, summaries: list[DailySummary]):
        self._pw.clear()
        if not summaries:
            today = datetime.now().date()
            summaries = [
                DailySummary(date=(today - timedelta(days=i)).isoformat(), total_tokens=0, total_sessions=0)
                for i in range(6, -1, -1)
            ]

        x = list(range(len(summaries)))
        heights = [s.total_tokens for s in summaries]
        max_h = max(heights) if max(heights) > 0 else 1

        ticks = [(i, self._format_date(s.date)) for i, s in enumerate(summaries)]

        brushes = []
        for i, h in enumerate(heights):
            if h == max(heights) and max_h > 0:
                brushes.append(pg.mkBrush("#D97706"))
            else:
                brushes.append(pg.mkBrush("#059669"))

        bar = BarGraphItem(x=x, height=heights, width=0.6, brushes=brushes)
        self._pw.addItem(bar)

        axis = self._pw.getAxis("bottom")
        axis.setTicks([ticks])

        if max_h > 0:
            prev = heights[-2] if len(heights) >= 2 else 1
            curr = heights[-1]
            if prev > 0:
                delta = ((curr - prev) / prev) * 100
                sign = "+" if delta >= 0 else ""
                self._delta.setText(f"{sign}{delta:.0f}% vs last wk")

    def _format_date(self, date_str: str) -> str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.strftime("%m/%d")
        except ValueError:
            return date_str[-5:]
```

---

### Task 11: 最近调用记录组件

**文件:**
- 创建: `src/components/call_history.py`

- [ ] **Step 1: 实现调用记录列表**

```python
# src/components/call_history.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from models import UsageLog
from datetime import datetime


class CallHistory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel("RECENT CALLS")
        title.setStyleSheet("color: #64748B; font-size: 9px; letter-spacing: 1px; border: none;")
        layout.addWidget(title)

        self._list = QVBoxLayout()
        self._list.setSpacing(3)
        layout.addLayout(self._list)
        layout.addStretch()

    def update_calls(self, logs: list[UsageLog]):
        # 清空旧条目
        while self._list.count():
            item = self._list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for log in logs[:3]:
            row = QWidget()
            row.setStyleSheet("background: #0E1223; border-radius: 5px; padding: 6px 10px;")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(10, 6, 10, 6)
            row_layout.setSpacing(0)

            inner = QWidget()
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(0, 0, 0, 0)

            top = QLabel(f"{log.model_name}")
            top.setStyleSheet("color: #94A3B8; font-size: 10px; font-family: 'Fira Code', monospace; border: none; background: transparent;")
            inner_layout.addWidget(top)

            bottom = QLabel(f"{log.token_count:,} tok · {self._time_ago(log.timestamp)}")
            bottom.setStyleSheet("color: #475569; font-size: 9px; border: none; background: transparent;")
            inner_layout.addWidget(bottom)

            row_layout.addWidget(inner)
            self._list.addWidget(row)

        self._list.addStretch()

    def _time_ago(self, ts) -> str:
        if ts is None:
            return ""
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        delta = datetime.now() - ts
        mins = int(delta.total_seconds() / 60)
        if mins < 1:
            return "just now"
        if mins < 60:
            return f"{mins}m ago"
        hours = mins // 60
        if hours < 24:
            return f"{hours}h ago"
        return f"{hours // 24}d ago"
```

---

### Task 12: 主面板

**文件:**
- 创建: `src/panel.py`

- [ ] **Step 1: 实现弹出面板主窗口**

```python
# src/panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from components.balance_card import BalanceCard
from components.model_selector import ModelSelector
from components.call_history import CallHistory
from charts import TokenChart
from models import Balance, ModelInfo, UsageLog, DailySummary


class PanelWidget(QWidget):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFixedSize(320, 400)
        self.setStyleSheet("background: #020617; border-radius: 8px;")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 0)
        layout.setSpacing(0)

        # --- 顶部状态栏 ---
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(4, 0, 4, 6)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet("color: #22C55E; font-size: 12px; border: none; background: transparent;")
        self._name_label = QLabel("TOKEN SURVEILLANCE")
        self._name_label.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700; border: none; background: transparent;")

        self._sync_label = QLabel("")
        self._sync_label.setStyleSheet("color: #475569; font-size: 9px; font-family: 'Fira Code', monospace; border: none; background: transparent;")

        header_layout.addWidget(self._status_dot)
        header_layout.addWidget(self._name_label)
        header_layout.addStretch()
        header_layout.addWidget(self._sync_label)
        layout.addWidget(header)

        # --- 分隔线 ---
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1a1f2e;")
        layout.addWidget(sep)

        layout.addSpacing(8)

        # --- 余额卡片 ---
        self.balance_card = BalanceCard()
        layout.addWidget(self.balance_card)

        layout.addSpacing(8)

        # --- 模型选择器 ---
        self.model_selector = ModelSelector()
        layout.addWidget(self.model_selector)

        layout.addSpacing(8)

        # --- 柱状图 ---
        self.chart = TokenChart()
        layout.addWidget(self.chart)

        layout.addSpacing(8)

        # --- 最近调用 ---
        self.call_history = CallHistory()
        layout.addWidget(self.call_history)

        layout.addSpacing(8)

        # --- 底部状态栏 ---
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(4, 4, 4, 10)

        self._api_status = QLabel("DeepSeek API · --")
        self._api_status.setStyleSheet("color: #475569; font-size: 9px; border: none; background: transparent;")

        refresh_btn = QPushButton("⭮ Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton { color: #475569; font-size: 9px; border: none; background: transparent; font-family: 'Fira Code', monospace; }
            QPushButton:hover { color: #94A3B8; }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        refresh_btn.setCursor(Qt.PointingHandCursor)

        footer_layout.addWidget(self._api_status)
        footer_layout.addStretch()
        footer_layout.addWidget(refresh_btn)
        layout.addWidget(footer)

    def update_balance(self, balance: Balance):
        if balance and balance.balance_infos:
            self.balance_card.update_balance(balance)
            self._set_api_status("DeepSeek API · Connected", "#22C55E")
        else:
            self.balance_card.clear()
            self._set_api_status("DeepSeek API · Error", "#EF4444")

    def update_models(self, models: list[ModelInfo]):
        self.model_selector.set_models(models)

    def update_chart(self, summaries: list[DailySummary]):
        self.chart.update_data(summaries)

    def update_calls(self, logs: list[UsageLog]):
        self.call_history.update_calls(logs)

    def update_daily_usage(self, tokens: int, sessions: int, est_days: int):
        self.balance_card.update_daily_usage(tokens, sessions, est_days)

    def set_sync_time(self, text: str):
        self._sync_label.setText(text)

    def _set_api_status(self, text: str, color: str):
        self._api_status.setText(text)
        self._status_dot.setStyleSheet(
            f"color: {color}; font-size: 12px; border: none; background: transparent;"
        )

    def set_error(self, msg: str):
        self._set_api_status(f"DeepSeek API · {msg}", "#EF4444")
        self._status_dot.setStyleSheet("color: #EF4444; font-size: 12px; border: none; background: transparent;")

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)
```

---

### Task 13: 主入口

**文件:**
- 创建: `main.py`

- [ ] **Step 1: 实现 main.py**

```python
# main.py
import sys
import os
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt

from src.config import AppConfig
from src.api import DeepSeekClient
from src.storage import Storage
from src.tray import TrayController
from src.panel import PanelWidget
from src.worker import RefreshWorker


def get_app_dir():
    path = os.path.join(os.environ["APPDATA"], "TokenSurveillance")
    os.makedirs(path, exist_ok=True)
    return path


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    app_dir = get_app_dir()
    config_path = os.path.join(app_dir, "config.json")
    db_path = os.path.join(app_dir, "usage.db")

    config = AppConfig.load(config_path)
    if not config.is_configured:
        from PyQt5.QtWidgets import QInputDialog
        key, ok = QInputDialog.getText(None, "Token Surveillance", "Enter DeepSeek API Key:")
        if ok and key.strip():
            config.api_key = key.strip()
            config.save(config_path)
        else:
            sys.exit(0)

    client = DeepSeekClient(config)
    storage = Storage(db_path)

    tray = TrayController()
    panel = PanelWidget()

    worker_ref = {"worker": None}

    def do_refresh():
        if worker_ref["worker"] and worker_ref["worker"].isRunning():
            return
        worker = RefreshWorker(client)
        worker_ref["worker"] = worker

        def on_done(balance, models, error):
            panel.set_sync_time(f"SYNC {datetime.now().strftime('%H:%M')}")
            if balance:
                panel.update_balance(balance)
                bi = balance.balance_infos[0] if balance.balance_infos else None
                if bi:
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    storage.upsert_daily_summary(today_str, 0, 0, models[0].id if models else "")
                    weekly = storage.get_weekly_summary(7)
                    panel.update_chart(weekly)
            else:
                panel.set_error(client.last_error)

            if models:
                panel.update_models(models)

            recent = storage.get_recent_calls(3)
            panel.update_calls(recent)

            panel.update_daily_usage(
                sum(s.total_tokens for s in storage.get_weekly_summary(1)),
                sum(s.total_sessions for s in storage.get_weekly_summary(1)),
                _estimate_days(balance),
            )

        worker.finished.connect(on_done)
        worker.start()

    def _estimate_days(balance) -> int:
        if not balance or not balance.balance_infos:
            return 0
        bi = balance.balance_infos[0]
        today_tokens = sum(s.total_tokens for s in storage.get_weekly_summary(1))
        if today_tokens == 0:
            return 999
        # Rough estimate: ¥0.002/token
        cost_per_token = 0.002 / 1_000_000
        daily_cost = today_tokens * cost_per_token
        if daily_cost <= 0:
            return 999
        return int(bi.total_balance / daily_cost)

    tray.refresh_requested.connect(do_refresh)
    tray.panel_toggle_requested.connect(lambda: panel.setVisible(not panel.isVisible()))

    # 弹出面板时自动刷新
    def on_visible_change():
        pass  # Panel shows with cached data; manual refresh updates

    # 自动刷新定时器
    if config.auto_refresh_minutes > 0:
        timer = QTimer()
        timer.timeout.connect(do_refresh)
        timer.start(config.auto_refresh_minutes * 60 * 1000)

    tray.show()
    do_refresh()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

---

### Task 14: 生成图标 + 集成验证

- [ ] **Step 1: 生成托盘图标**

```bash
python scripts/generate_icon.py
```

- [ ] **Step 2: 启动应用验证**

```bash
python main.py
```

验证清单:
1. 托盘图标出现（绿色 S + 黑底）
2. 首次运行弹出 API Key 输入框
3. 右键菜单显示 "显示面板 / 立即刷新 / 设置 / 退出"
4. 左键单击弹出面板
5. 面板显示余额、模型标签、柱状图、调用记录
6. 点击 Refresh 按钮更新数据
7. 点击面板外部区域自动隐藏
8. 鼠标悬停柱状图显示 tooltip (需 pyqtgraph 信号连接)

---

## 验证步骤

1. `python -m pytest tests/ -v` — 全部测试通过
2. `python main.py` — 托盘 + 面板正常
3. 检查 `%APPDATA%/TokenSurveillance/` — `config.json` 和 `usage.db` 已创建
4. 检查 `usage.db` — `usage_log` 和 `daily_summary` 表存在
