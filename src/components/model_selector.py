from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from ..models import ModelInfo


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
