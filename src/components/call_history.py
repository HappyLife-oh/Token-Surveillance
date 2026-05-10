from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from ..models import UsageLog
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
        while self._list.count():
            item = self._list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for log in logs[:3]:
            row = QWidget()
            row.setStyleSheet("background: #0E1223; border-radius: 5px;")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(10, 6, 10, 6)
            row_layout.setSpacing(0)

            top = QLabel(f"{log.model_name}")
            top.setStyleSheet("color: #94A3B8; font-size: 10px; font-family: 'Fira Code', monospace; border: none; background: transparent;")
            row_layout.addWidget(top)

            bottom = QLabel(f"{log.token_count:,} tok · {self._time_ago(log.timestamp)}")
            bottom.setStyleSheet("color: #475569; font-size: 9px; border: none; background: transparent;")
            row_layout.addWidget(bottom)

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
