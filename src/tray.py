from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
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
        self._quit_action.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)

    def _load_icon(self) -> QIcon:
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
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
