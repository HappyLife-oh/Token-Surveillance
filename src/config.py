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
