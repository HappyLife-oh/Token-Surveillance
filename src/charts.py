import pyqtgraph as pg
from pyqtgraph import BarGraphItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from .models import DailySummary
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

        if max_h > 0 and len(heights) >= 2:
            prev = heights[-2]
            curr = heights[-1]
            if prev > 0:
                delta = ((curr - prev) / prev) * 100
                sign = "+" if delta >= 0 else ""
                self._delta.setText(f"{sign}{delta:.0f}% vs yesterday")

    def _format_date(self, date_str: str) -> str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.strftime("%m/%d")
        except ValueError:
            return date_str[-5:]
