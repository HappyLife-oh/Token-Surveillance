from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QColor

from .components.balance_card import BalanceCard
from .components.model_selector import ModelSelector
from .components.call_history import CallHistory
from .charts import TokenChart
from .models import Balance, ModelInfo, UsageLog, DailySummary


class PanelWidget(QWidget):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFixedSize(340, 420)

    def _setup_ui(self):
        # Outer container with border and shadow
        outer = QWidget(self)
        outer.setGeometry(0, 0, 340, 420)
        outer.setStyleSheet("""
            QWidget#panelContainer {
                background: #020617;
                border: 1px solid #1E293B;
                border-radius: 10px;
            }
        """)
        outer.setObjectName("panelContainer")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        outer.setGraphicsEffect(shadow)

        layout = QVBoxLayout(outer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Draggable Header Area ---
        header = QWidget()
        header.setObjectName("dragHeader")
        header.setStyleSheet("""
            QWidget#dragHeader {
                background: transparent;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 8)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet("color: #22C55E; font-size: 10px; border: none; background: transparent;")
        self._name_label = QLabel("TOKEN SURVEILLANCE")
        self._name_label.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; border: none; background: transparent;")

        self._sync_label = QLabel("")
        self._sync_label.setStyleSheet("color: #475569; font-size: 9px; font-family: 'Consolas', monospace; border: none; background: transparent;")

        header_layout.addWidget(self._status_dot)
        header_layout.addSpacing(6)
        header_layout.addWidget(self._name_label)
        header_layout.addStretch()
        header_layout.addWidget(self._sync_label)

        layout.addWidget(header)

        # --- Header divider ---
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1E293B; margin: 0 12px;")
        layout.addWidget(sep)

        # --- Scrollable content area ---
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 10, 16, 8)
        content_layout.setSpacing(8)

        self.balance_card = BalanceCard()
        content_layout.addWidget(self.balance_card)

        self.model_selector = ModelSelector()
        content_layout.addWidget(self.model_selector)

        self.chart = TokenChart()
        content_layout.addWidget(self.chart)

        self.call_history = CallHistory()
        content_layout.addWidget(self.call_history)

        layout.addWidget(content)

        # --- Footer ---
        footer = QWidget()
        footer.setStyleSheet("background: transparent; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 6, 16, 12)

        self._api_status = QLabel("DeepSeek API · --")
        self._api_status.setStyleSheet("color: #475569; font-size: 9px; border: none; background: transparent;")

        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                color: #64748B; font-size: 9px; border: 1px solid #1E293B;
                border-radius: 4px; padding: 4px 10px;
                background: transparent; font-family: 'Consolas', monospace;
            }
            QPushButton:hover { color: #94A3B8; border-color: #334155; background: #0F172A; }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        refresh_btn.setCursor(Qt.PointingHandCursor)

        footer_layout.addWidget(self._api_status)
        footer_layout.addStretch()
        footer_layout.addWidget(refresh_btn)
        layout.addWidget(footer)

        # Make header draggable
        header.mousePressEvent = self._mouse_press
        header.mouseMoveEvent = self._mouse_move
        header.mouseReleaseEvent = self._mouse_release

    def _mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _mouse_move(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def _mouse_release(self, event):
        self._drag_pos = None

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
            f"color: {color}; font-size: 10px; border: none; background: transparent;"
        )

    def set_error(self, msg: str):
        self._set_api_status(f"DeepSeek API · {msg}", "#EF4444")

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)
