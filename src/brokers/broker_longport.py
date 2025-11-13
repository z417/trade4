from typing import Any, Dict, List, Literal
from datetime import datetime, date
from dotenv import dotenv_values
from longport.openapi import (
    Config,
    Language,
    PushCandlestickMode,
    QuoteContext,
    TradeContext,
)
from core.broker import Broker
from core.data_models import WatchlistSecurityModel


class BrokerLongport(Broker):
    """长桥"""

    def __init__(self, credentials: str):
        super().__init__()
        self.env: Dict = dotenv_values(credentials)

    def connect(
        self,
        language=Language.ZH_CN,
        enable_overnight=True,
        push_candlestick_mode=PushCandlestickMode.Realtime,
        enable_print_quote_packages=False,
    ):
        self.config: Config = Config(
            app_key=self.env["LONGPORT_APP_KEY"],
            app_secret=self.env["LONGPORT_APP_SECRET"],
            access_token=self.env["LONGPORT_ACCESS_TOKEN"],
            language=language,
            enable_overnight=enable_overnight,
            push_candlestick_mode=push_candlestick_mode,
            enable_print_quote_packages=enable_print_quote_packages,
            log_path=self.env["LONGPORT_LOG_PATH"] or None,
        )
        self.quote_ctx: QuoteContext = QuoteContext(self.config)
        self.trade_ctx: TradeContext = TradeContext(self.config)
        self.refresh_watchlist()
        return self

    def refresh_watchlist(self):
        self.watchlist = self.quote_ctx.watchlist()

    def get_watchlist_by_group(self, group_name: str):
        tmp = next(
            filter(
                lambda x: x.name == group_name,
                self.watchlist,
            ),
        )
        return [
            WatchlistSecurityModel(
                watchlistSecurity.symbol,
                watchlistSecurity.market,
                watchlistSecurity.name,
                watchlistSecurity.watched_price,
                watchlistSecurity.watched_at,
                tmp.id,
                tmp.name,
            )
            for watchlistSecurity in tmp.securities
        ]

    def get_watchlist(self):
        return self.get_watchlist_by_group("all")

    def get_holdings(self):
        return self.get_watchlist_by_group("holdings")

    def get_watchlistGroups(self):
        return [{"id": x.id, "name": x.name} for x in self.watchlist]

    def get_account_balance(self):
        return self.trade_ctx.account_balance()

    def get_stock_static_info(self, symbols: List[str]):
        return self.quote_ctx.static_info(symbols)
