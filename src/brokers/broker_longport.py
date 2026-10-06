from typing import List, Optional
from decimal import Decimal
import pandas as pd
from longport.openapi import (
    Config,
    Language,
    PushCandlestickMode,
    QuoteContext,
    TradeContext,
    Period,
    AdjustType,
)
from core import Broker, WatchlistSecurityModel, SecurityStaticInfoModel


class BrokerLongport(Broker):
    """长桥"""

    def __init__(self, conf):
        super().__init__()
        self.conf = conf
        self.config: Optional[Config] = None
        self.quote_ctx: Optional[QuoteContext] = None
        self.trade_ctx: Optional[TradeContext] = None

    def connect(
        self,
        language=Language.ZH_CN,
        enable_overnight=True,
        push_candlestick_mode=PushCandlestickMode.Realtime,
        enable_print_quote_packages=False,
    ):
        self.config: Config = Config(
            app_key=self.conf.longport_app_key,
            app_secret=self.conf.longport_app_secret,
            access_token=self.conf.longport_access_token,
            language=language,
            enable_overnight=enable_overnight,
            push_candlestick_mode=push_candlestick_mode,
            enable_print_quote_packages=enable_print_quote_packages,
            log_path=self.conf.longport_log_path or None,
        )
        self.quote_ctx: QuoteContext = QuoteContext(self.config)
        self.trade_ctx: TradeContext = TradeContext(self.config)
        return self

    def _ensure_quote_ctx(self) -> QuoteContext:
        if self.quote_ctx is None:
            raise RuntimeError("QuoteContext 未初始化，请先调用 connect()")
        return self.quote_ctx

    def _ensure_trade_ctx(self) -> TradeContext:
        if self.trade_ctx is None:
            raise RuntimeError("TradeContext 未初始化，请先调用 connect()")
        return self.trade_ctx

    def get_watchlist_by_group(self, group_name: str) -> List[WatchlistSecurityModel]:
        ctx = self._ensure_quote_ctx()
        group = next((x for x in ctx.watchlist() if x.name == group_name), None)
        if group is None:
            return []
        return [
            WatchlistSecurityModel(
                symbol=watchlistSecurity.symbol,
                market=watchlistSecurity.market,
                name=watchlistSecurity.name,
                watched_price=watchlistSecurity.watched_price,
                watched_at=watchlistSecurity.watched_at,
                group_id=group.id,
                group_name=group.name,
            )
            for watchlistSecurity in group.securities
        ]

    @property
    def watchlist(self):
        return self.get_watchlist_by_group("all")

    @property
    def holdings(self):
        return self.get_watchlist_by_group("holdings")

    @property
    def watchlist_groups(self):
        ctx = self._ensure_quote_ctx()
        return [{"id": x.id, "name": x.name} for x in ctx.watchlist()]

    @property
    def watchlistGroups(self):
        return self.watchlist_groups

    @property
    def account_balance(self):
        ctx = self._ensure_trade_ctx()
        return ctx.account_balance()

    def get_stock_static_info(self, symbols: List[str]):
        ctx = self._ensure_quote_ctx()
        batches = [symbols[i : i + 500] for i in range(0, len(symbols), 500)]  # 每次限流500个
        return [
            SecurityStaticInfoModel(
                symbol=x.symbol,
                name=x.name_cn,
                exchange=x.exchange,
                currency=x.currency,
                lot_size=x.lot_size,
                total_shares=x.total_shares,
                circulating_shares=x.circulating_shares,
                eps=x.eps,
                eps_ttm=x.eps_ttm,
                bps=x.bps,
                dividend_yield=x.dividend_yield,
                stock_derivatives=x.stock_derivatives,
                board=x.board,
            )
            for batch in batches
            for x in ctx.static_info(batch)
        ]

    def get_history_candlesticks(
        self, symbol: str, count: int = 100
    ) -> pd.DataFrame:
        """
        获取指定标的的历史日K线（前复权）

        :param symbol: 标的代码，长桥格式如 '000001.SZ'
        :param count: 获取K线数量，默认100根
        :return: 包含 symbol, date, open, high, low, close, volume, turnover 的标准 DataFrame
        """
        ctx = self._ensure_quote_ctx()
        candlesticks = ctx.candlesticks(
            symbol=symbol,
            period=Period.Day,
            count=count,
            adjust_type=AdjustType.ForwardAdjust,
        )
        records = []
        for c in candlesticks:
            ts = c.timestamp
            if isinstance(ts, (int, float)):
                dt = pd.to_datetime(ts, unit="s")
            else:
                dt = pd.to_datetime(ts)
            records.append(
                {
                    "symbol": symbol,
                    "date": dt,
                    "open": Decimal(str(c.open)),
                    "high": Decimal(str(c.high)),
                    "low": Decimal(str(c.low)),
                    "close": Decimal(str(c.close)),
                    "volume": int(c.volume),
                    "turnover": Decimal(str(c.turnover)),
                }
            )
        return pd.DataFrame(records)
