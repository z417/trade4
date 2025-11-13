from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class WatchlistSecurityModel:
    symbol: str = field(
        # default="",
        metadata={
            "description": "标的代码，使用 ticker.region 格式，例如：700.HK",
            "pattern": r"^[A-Z0-9]{1,10}\.(HK|US|SH|SZ)$",
        },
    )
    market: Any
    name: str
    watched_price: Optional[Decimal]
    watched_at: datetime
    group_id: int
    group_name: str
