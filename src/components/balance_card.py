from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from ..models import Balance


class BalanceCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget#balanceCard {
                background: #0E1223;
                border-left: 3px solid #059669;
                border-radius: 8px;
                border: 1px solid #1E293B;
            }
        """)
        self.setObjectName("balanceCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Title row: label + model pill
        title_row = QHBoxLayout()
        title_row.setSpacing(6)

        self._label_title = QLabel("BALANCE")
        self._label_title.setStyleSheet("color: #64748B; font-size: 9px; letter-spacing: 1.5px; border: none; background: transparent;")

        self._model_pill = QLabel("DeepSeek")
        self._model_pill.setStyleSheet("""
            color: #059669; font-size: 8px; letter-spacing: 0.5px;
            border: 1px solid #05966940; border-radius: 3px;
            padding: 1px 6px; background: #05966910;
        """)

        title_row.addWidget(self._label_title)
        title_row.addWidget(self._model_pill)
        title_row.addStretch()
        layout.addLayout(title_row)

        # Amount row
        self._balance_amount = QLabel("--")
        self._balance_amount.setStyleSheet(
            "color: #F1F5F9; font-size: 36px; font-weight: 800; "
            "font-family: 'Consolas', monospace; border: none; background: transparent;"
        )
        layout.addWidget(self._balance_amount)

        # Info row
        self._info_row = QLabel("Today -- tok  ·  -- sessions  ·  Est. --d")
        self._info_row.setStyleSheet("color: #64748B; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(self._info_row)

    def update_balance(self, balance: Balance):
        bi = balance.balance_infos[0] if balance.balance_infos else None
        if bi:
            self._balance_amount.setText(f"¥{bi.total_balance:.2f}")
            if bi.total_balance < 1.0:
                border_color = "#EF4444"
            elif bi.total_balance < 10.0:
                border_color = "#D97706"
            else:
                border_color = "#059669"
            self.setStyleSheet(
                f"QWidget#balanceCard {{ background: #0E1223; border-left: 3px solid {border_color}; "
                f"border-radius: 8px; border: 1px solid #1E293B; }}"
            )

    def update_daily_usage(self, tokens_today: int, sessions_today: int, estimated_days: int):
        tokens_str = f"{tokens_today / 1e6:.2f}M" if tokens_today >= 1e6 else f"{tokens_today:,}"
        self._info_row.setText(
            f"Today {tokens_str} tok  ·  {sessions_today} sessions  ·  Est. ~{estimated_days}d"
        )

    def clear(self):
        self._balance_amount.setText("--")
        self._info_row.setText("Today -- tok  ·  -- sessions  ·  Est. --d")
