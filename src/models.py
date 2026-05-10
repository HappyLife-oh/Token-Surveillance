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
