from typing import List, Literal, Dict
from datetime import date, datetime
from utils.typevar import *
from brokers.IBroker import IBroker


class QuoteService:
    def __init__(self, broker: IBroker, market):
        self.broker = broker
        self.market = market
        self.broker.connect()

    @property
    def allWatchlist(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        return self.broker.allWatchlist

    @property
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], int | str]]:
        """获取所有分组"""
        return self.broker.watchlistGroups

    @property
    def holdings(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        return self.broker.holdings

    def get_watchlist_by_group(self, group_name: str) -> List[TWatchlistSecurity]:
        """获取指定组名下的所有股票"""
        return self.broker.get_watchlist_by_group(group_name)

    def pull_static_info(self, symbols: List[str]) -> List[TSecurityStaticInfo]:
        """获取标的基础信息"""
        return self.broker.pull_static_info(symbols)

    def pull_quote(self, symbols: List[str]) -> List[TSecurityQuote]:
        """获取标的行情"""
        return self.broker.pull_quote(symbols)

    def pull_depth(self, symbol: str) -> Dict[Literal["bids", "asks"], List[TDepth]]:
        """获取标的深度"""
        return self.broker.pull_depth(symbol)

    def pull_intraday(self, symbol: str) -> List[TIntradayLine]:
        """获取标的分时"""
        return self.broker.pull_intraday(symbol)

    def pull_history_candlesticks_by_offset(
        self,
        symbol: str,
        period: EPeriod,  # k 线周期
        adjust_type: Literal["NoAdjust", "ForwardAdjust"],  # 复权类型
        forward: bool = False,  # True: 向最新，False: 向历史
        count: int = 10,  # 查询数量，填写范围 [1,1000]，为空时默认查询 10 条
        time: Optional[datetime] = None,  # 偏移点时间
    ) -> List[TCandlesticks]:
        """按时间偏移获取标的历史K线"""
        return self.broker.pull_history_candlesticks_by_offset(
            symbol,
            period,
            adjust_type,
            forward,
            count,
            time,
        )

    def pull_history_candlesticks_by_date(
        self,
        symbol: str,
        period: EPeriod,
        adjust_type: Literal["NoAdjust", "ForwardAdjust"],
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[TCandlesticks]:
        """按日期获取标的历史K线"""
        return self.broker.pull_history_candlesticks_by_date(
            symbol,
            period,
            adjust_type,
            start,
            end,
        )

    def pull_capital_flow(
        self, symbol: str
    ) -> List[Dict[Literal["inflow", "timestamp"], Decimal | datetime]]:
        """获取标的当日的资金流向(每分钟)"""
        return self.broker.pull_capital_flow(symbol)

    def pull_capital_distribution(self, symbol: str) -> Dict[
        Literal[
            "timestamp",
            "capital_in",
            "capital_out",
        ],
        datetime
        | Dict[
            Literal[
                "large",
                "medium",
                "small",
            ],
            Decimal,
        ],
    ]:
        """获取标的当日的资金分布"""
        return self.broker.pull_capital_distribution(symbol)

    def pull_calc_indexes(self):
        """获取标的计算指标"""
        return self.broker.pull_calc_indexes()

    def pull_candlesticks(self):
        """获取标的 K 线"""
        return self.broker.pull_candlesticks()
