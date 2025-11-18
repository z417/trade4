from dataclasses import dataclass, field, fields
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal
from .common_fields import *


@dataclass
class BaseDataclass:
    def __repr__(self) -> str:
        lines = [f"{self.__class__.__name__}("]
        for f in sorted(fields(self), key=lambda x: x.metadata.get("priority", 99)):
            lines.append(
                f"\t{f.metadata.get("desc", f.name)}: {getattr(self, f.name)!r}"
            )
        lines.append(")")
        return "\n".join(lines)


@dataclass(repr=False)
class WatchlistSecurityModel(BaseDataclass):
    """自选标的"""

    watched_at: datetime = field(metadata={"desc": "自选日"})
    watched_price: Optional[Decimal] = field(metadata={"desc": "自选价"})
    group_id: int = group_id
    group_name: str = group_name
    name: str = name_cn
    symbol: str = symbol
    market: Any = market


@dataclass(repr=False)
class SecurityStaticInfoModel(BaseDataclass):
    """标的基本信息"""

    lot_size: int = field(metadata={"desc": "每手数量", "priority": 2})
    total_shares: int = field(metadata={"desc": "总股本", "priority": 2})
    circulating_shares: int = field(metadata={"desc": "流通股", "priority": 2})
    symbol: str = symbol
    name: str = name_cn
    exchange: str = exchange
    currency: str = currency
    eps: Decimal = eps
    eps_ttm: Decimal = eps_ttm
    bps: Decimal = bps
    dividend_yield: Decimal = dividend_yield
    stock_derivatives: Any = stock_derivatives
    board: Any = board
