from typing import Dict, List
from longport.openapi import (
    Config,
    Language,
    PushCandlestickMode,
    QuoteContext,
    TradeContext,
    HttpClient,
)
from core import Broker, WatchlistSecurityModel, SecurityStaticInfoModel


class BrokerLongport(Broker):
    """长桥"""

    def __init__(self, credentials: Dict):
        super().__init__()
        self.env: Dict = credentials

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
        self.http_cli: HttpClient = HttpClient.from_env()
        return self

    def get_watchlist_by_group(self, group_name: str):
        tmp = next(
            filter(
                lambda x: x.name == group_name,
                self.quote_ctx.watchlist(),
            ),
        )
        return [
            WatchlistSecurityModel(
                symbol=watchlistSecurity.symbol,
                market=watchlistSecurity.market,
                name=watchlistSecurity.name,
                watched_price=watchlistSecurity.watched_price,
                watched_at=watchlistSecurity.watched_at,
                group_id=tmp.id,
                group_name=tmp.name,
            )
            for watchlistSecurity in tmp.securities
        ]

    @property
    def watchlist(self):
        return self.get_watchlist_by_group("all")

    @property
    def holdings(self):
        return self.get_watchlist_by_group("holdings")

    @property
    def watchlistGroups(self):
        return [{"id": x.id, "name": x.name} for x in self.quote_ctx.watchlist()]

    @property
    def account_balance(self):
        return self.trade_ctx.account_balance()

    def get_stock_static_info(self, symbols: List[str]):
        batches = [
            symbols[i : i + 500] for i in range(0, len(symbols), 500)
        ]  # 每次限流500个
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
            for x in self.quote_ctx.static_info(batch)
        ]
