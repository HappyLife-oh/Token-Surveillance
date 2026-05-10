import httpx
from .config import AppConfig
from .models import Balance, ModelInfo


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
