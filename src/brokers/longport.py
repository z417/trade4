from typing import Any, Dict, List, Literal
from datetime import datetime, date
from dotenv import dotenv_values
from longport.openapi import (
    Config,
    Language,
    PushCandlestickMode,
    QuoteContext,
    Period,
    AdjustType,
)
from brokers.IBroker import IBroker
from utils.typevar import *
from utils.typevar import Any


class LongportBroker(IBroker):
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
    ) -> None:
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
                symbol=watchlistSecurity.symbol,
                name=watchlistSecurity.name,
                market=watchlistSecurity.market,
                watched_price=watchlistSecurity.watched_price,
                watched_at=watchlistSecurity.watched_at,
                group_id=tmp.id,
                group_name=tmp.name,
            )
            for watchlistSecurity in tmp.securities
        ]

    @property
    def allWatchlist(self) -> List[TWatchlistSecurity]:
        return self.get_watchlist_by_group("all")

    @property
    def holdings(self) -> List[TWatchlistSecurity]:
        return self.get_watchlist_by_group("holdings")

    @property
    def watchlistGroups(
        self,
    ) -> List[Dict[Literal["id", "name"], int | str]]:
        return [
            {
                "id": watchlist.id,
                "name": watchlist.name,
            }
            for watchlist in self.watchlist
        ]

    def pull_static_info(self, symbols: List[str]) -> List[TSecurityStaticInfo]:
        return [
            TSecurityStaticInfo(
                symbol=ssi.symbol,
                name=ssi.name_cn or ssi.name_en or ssi.name_hk,
                exchange=ssi.exchange,
                currency=ssi.currency,
                lot_size=ssi.lot_size,
                total_shares=ssi.total_shares,
                circulating_shares=ssi.circulating_shares,
                eps=ssi.eps,
                eps_ttm=ssi.eps_ttm,
                bps=ssi.bps,
                dividend_yield=ssi.dividend_yield,
                board=ssi.board,
            )
            for ssi in self.quote_ctx.static_info(symbols)
        ]

    def pull_quote(self, symbols: List[str]) -> List[TSecurityQuote]:
        def _type_convert_(item) -> TPrePostQuote | None:
            return (
                TPrePostQuote(
                    last_done=item.last_done,
                    prev_close=item.prev_close,
                    high=item.high,
                    low=item.low,
                    timestamp=item.timestamp,
                    volume=item.volume,
                    turnover=item.turnover,
                )
                if item
                else None
            )

        return [
            TSecurityQuote(
                symbol=sq.symbol,
                last_done=sq.last_done,
                prev_close=sq.prev_close,
                open=sq.open,
                high=sq.high,
                low=sq.low,
                timestamp=sq.timestamp,
                volume=sq.volume,
                turnover=sq.turnover,
                trade_status=sq.trade_status,
                pre_market_quote=_type_convert_(sq.pre_market_quote),
                post_market_quote=_type_convert_(sq.post_market_quote),
                overnight_quote=_type_convert_(sq.overnight_quote),
            )
            for sq in self.quote_ctx.quote(symbols)
        ]

    def pull_depth(self, symbol: str) -> Dict[Literal["bids", "asks"], List[TDepth]]:
        def _type_convert_(depths: List) -> List[TDepth]:
            return [
                TDepth(
                    position=a.position,
                    price=a.price,
                    volume=a.volume,
                    order_num=a.order_num,
                )
                for a in depths
            ]

        depths = self.quote_ctx.depth(symbol)
        return {
            "asks": _type_convert_(depths.asks),  # 卖盘
            "bids": _type_convert_(depths.bids),  # 买盘
        }

    def pull_intraday(self, symbol: str) -> List[TIntradayLine]:
        return [
            TIntradayLine(
                price=i.price,
                timestamp=i.timestamp,
                volume=i.volume,
                turnover=i.turnover,
                avg_price=i.avg_price,
            )
            for i in self.quote_ctx.intraday(symbol)
        ]

    def pull_history_candlesticks_by_offset(
        self,
        symbol: str,
        period: EPeriod,
        adjust_type: Literal["NoAdjust", "ForwardAdjust"],
        forward: bool,
        count: int,
        time: Optional[datetime] = None,
    ) -> List[TCandlesticks]:
        return [
            TCandlesticks(
                close=cs.close,
                open=cs.open,
                low=cs.low,
                high=cs.high,
                volume=cs.volume,
                turnover=cs.turnover,
                timestamp=cs.timestamp,
            )
            for cs in self.quote_ctx.history_candlesticks_by_offset(
                symbol,
                getattr(Period, period.name),
                getattr(AdjustType, adjust_type),
                forward,
                count,
                time,
            )
        ]

    def pull_history_candlesticks_by_date(
        self,
        symbol: str,
        period: EPeriod,
        adjust_type: Literal["NoAdjust", "ForwardAdjust"],
        start: Optional[date],
        end: Optional[date],
    ) -> List[TCandlesticks]:
        return [
            TCandlesticks(
                close=cs.close,
                open=cs.open,
                low=cs.low,
                high=cs.high,
                volume=cs.volume,
                turnover=cs.turnover,
                timestamp=cs.timestamp,
            )
            for cs in self.quote_ctx.history_candlesticks_by_date(
                symbol,
                getattr(Period, period.name),
                getattr(AdjustType, adjust_type),
                start,
                end,
            )
        ]

    def pull_capital_flow(
        self, symbol: str
    ) -> List[Dict[Literal["inflow", "timestamp"], Decimal | datetime]]:
        return [
            {"inflow": cf.inflow, "timestamp": cf.timestamp}
            for cf in self.quote_ctx.capital_flow(symbol)
        ]

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
        cd = self.quote_ctx.capital_distribution(symbol)
        return {
            "timestamp": cd.timestamp,
            "capital_in": {
                "large": cd.capital_in.large,
                "medium": cd.capital_in.medium,
                "small": cd.capital_in.small,
            },
            "capital_out": {
                "large": cd.capital_in.large,
                "medium": cd.capital_in.medium,
                "small": cd.capital_in.small,
            },
        }

    def pull_calc_indexes(self):
        return self.quote_ctx.calc_indexes()

    def pull_candlesticks(self, *args: Any, **kw: Any):
        return self.quote_ctx.candlesticks()
