from typing import Dict, List
from dotenv import dotenv_values
from longport.openapi import Config, Language, PushCandlestickMode, QuoteContext
from brokers.IBroker import IBroker
from utils.typevar import TWatchlistSecurity


class LongportBroker(IBroker):
    """长桥"""

    def __init__(self, credentials: str):
        super().__init__()
        self.env: Dict = dotenv_values(credentials)

    def connect(
        self,
        enable_overnight=True,
        enable_print_quote_packages=False,
    ) -> None:
        self.config: Config = Config(
            app_key=self.env["LONGPORT_APP_KEY"],
            app_secret=self.env["LONGPORT_APP_SECRET"],
            access_token=self.env["LONGPORT_ACCESS_TOKEN"],
            language=Language.ZH_CN,
            enable_overnight=enable_overnight,
            push_candlestick_mode=PushCandlestickMode.Realtime,
            enable_print_quote_packages=enable_print_quote_packages,
            log_path=self.env["LONGPORT_LOG_PATH"],
        )
        self.quote_ctx: QuoteContext = QuoteContext(self.config)
        self.refresh_watchlist()

    def refresh_watchlist(self) -> None:
        self.watchlist = self.quote_ctx.watchlist()

    def get_watchlist_by_group(self, group_name: str) -> List[TWatchlistSecurity]:
        tmp = next(
            filter(
                lambda x: x.name == group_name,
                self.watchlist,
            ),
        )
        return [
            TWatchlistSecurity(
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

    def get_watchlist(self) -> List[TWatchlistSecurity]:
        return self.get_watchlist_by_group("all")
