from PyQt5.QtCore import QThread, pyqtSignal
from .api import DeepSeekClient
from .models import Balance, ModelInfo


class RefreshWorker(QThread):
    data_ready = pyqtSignal(object, object, str)  # balance, models, error

    def __init__(self, client: DeepSeekClient, parent=None):
        super().__init__(parent)
        self.client = client

    def run(self):
        try:
            balance = self.client.get_balance()
            models = self.client.get_models()
            self.data_ready.emit(balance, models, self.client.last_error)
        except Exception as e:
            self.data_ready.emit(None, [], str(e))
