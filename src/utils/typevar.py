from dataclasses import dataclass
from typing import Optional, Type, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


@dataclass(kw_only=True)
class TSecurity:
    symbol: str  # 标的代码
    name: str


@dataclass(kw_only=True)
class TPrePostQuote:
    last_done: Decimal  # 最新价
    prev_close: Decimal  # 上一个交易阶段的收盘价
    high: Decimal  # 最高价
    low: Decimal  # 最低价
    timestamp: datetime  # 最新成交的时间戳
    volume: int  # 成交量
    turnover: Decimal  # 成交额


@dataclass(kw_only=True)
class TWatchlistSecurity(TSecurity):
    """关注的标的"""

    market: Any
    watched_price: Optional[Decimal]
    watched_at: Optional[datetime]
    group_id: int = -1
    group_name: str = "未命名"


@dataclass(kw_only=True)
class TSecurityStaticInfo(TSecurity):
    """标的基础信息"""

    exchange: str  # 标的所属交易所
    currency: str  # 交易币种
    lot_size: int  # 每手数量
    total_shares: int  # 总股本
    circulating_shares: int  # 流通股本
    eps: Decimal  # 每股收益
    eps_ttm: Decimal  # 每股盈利 (TTM)
    bps: Decimal  # 每股净资产
    dividend_yield: Decimal  # 股息
    board: Type  # 标的所属板块


@dataclass(kw_only=True)
class TSecurityQuote(TPrePostQuote):
    """标的实时行情"""

    symbol: str  # 标的代码
    open: Decimal  # 今日开盘价
    trade_status: Type  # 交易状态
    pre_market_quote: Optional[TPrePostQuote]  # 美股盘前交易行情
    post_market_quote: Optional[TPrePostQuote]  # 美股盘后交易行情
    overnight_quote: Optional[TPrePostQuote]  # 美股夜盘交易行情


@dataclass(kw_only=True)
class TDepth:
    """买卖盘口"""

    position: int  # 档位
    price: Optional[Decimal]  # 价格
    volume: int  # 挂单量
    order_num: int  # 订单数量


@dataclass(kw_only=True)
class TIntradayLine:
    """当日分时"""

    price: Decimal  # 当前分钟的收盘价格
    timestamp: datetime  # 当前分钟的开始时间
    volume: int  # 成交量
    turnover: Decimal  # 成交额
    avg_price: Decimal  # 均价


class EPeriod(Enum):
    """k线周期"""

    Min_1 = 1
    Min_2 = 2
    Min_3 = 3
    Min_5 = 5
    Min_10 = 10
    Min_15 = 15
    Min_20 = 20
    Min_30 = 30
    Min_45 = 45
    Min_60 = 60
    Min_120 = 120
    Min_180 = 180
    Min_240 = 240
    Day = 1000
    Week = 2000
    Month = 3000
    Quarter = 3500
    Year = 4000


@dataclass(kw_only=True)
class TCandlesticks:
    """k线"""

    close: Decimal  # 当前周期收盘价
    open: Decimal  # 当前周期开盘价
    low: Decimal  # 当前周期最低价
    high: Decimal  # 当前周期最高价
    volume: int  # 当前周期成交量
    turnover: Decimal  # 当前周期成交额
    timestamp: datetime  # 当前周期的时间戳
