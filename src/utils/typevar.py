from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class TWatchlistSecurity:
    symbol: str
    market: Any
    name: str
    watched_price: Optional[Decimal]
    watched_at: datetime
    group_id: int
    group_name: str
