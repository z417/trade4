from typing import Any, Literal
from decimal import Decimal
from longbridge.openapi import (
    Config,
    AsyncQuoteContext,
    AsyncTradeContext,
    Period,
    AdjustType,
)
import pandas as pd
from core import Broker, WatchlistSecurityModel, SecurityStaticInfoModel

async def create_longbridge_broker() -> Broker:
    """长桥 API 闭包工厂：封存连接状态，返回纯函数字典"""

    # --- 1. 状态封存在闭包上下文中 ---
    config = Config.from_apikey_env()
    quote_ctx = AsyncQuoteContext.create(config)
    trade_ctx = AsyncTradeContext.create(config)

    # --- 2. 业务纯函数实现 ---
    async def get_watchlist_groups() -> list[dict[Literal["id", "name"], int | str]]:
        return [{"id": x.id, "name": x.name} for x in await quote_ctx.watchlist()]

    async def get_watchlist_by_group(group_name: str) -> list[WatchlistSecurityModel]:
        target_group = next((x for x in await quote_ctx.watchlist() if x.name == group_name), None)
        if not target_group:
            return []

        return [
            WatchlistSecurityModel(
                symbol=sec.symbol,
                market=sec.market,
                name=sec.name,
                watched_price=Decimal(str(sec.watched_price)) if sec.watched_price else None,
                watched_at=sec.watched_at,
                group_id=target_group.id,
                group_name=target_group.name,
            )
            for sec in target_group.securities
        ]

    async def get_watchlist() -> list[WatchlistSecurityModel]:
        return await get_watchlist_by_group("all")

    async def get_holdings() -> list[WatchlistSecurityModel]:
        return await get_watchlist_by_group("holdings")

    async def get_account_balance() -> Any:
        return await trade_ctx.account_balance()

    async def get_stock_static_info(symbols: list[str]) -> list[SecurityStaticInfoModel]:
        batches = [symbols[i : i + 500] for i in range(0, len(symbols), 500)]
        return [
            SecurityStaticInfoModel(
                symbol=x.symbol,
                name=x.name_cn,
                exchange=x.exchange,
                currency=x.currency,
                lot_size=x.lot_size,
                total_shares=x.total_shares,
                circulating_shares=x.circulating_shares,
                eps=Decimal(str(x.eps)) if x.eps is not None else Decimal("0"),
                eps_ttm=Decimal(str(x.eps_ttm)) if x.eps_ttm is not None else Decimal("0"),
                bps=Decimal(str(x.bps)) if x.bps is not None else Decimal("0"),
                dividend_yield=Decimal(str(x.dividend_yield)) if x.dividend_yield is not None else Decimal("0"),
                stock_derivatives=x.stock_derivatives,
                board=x.board,
            )
            for batch in batches
            for x in await quote_ctx.static_info(batch)
        ]

    async def get_history_candlesticks(symbol: str, count: int = 100) -> pd.DataFrame:
        """获取指定标的的历史日K线（前复权）"""
        candlesticks = await quote_ctx.candlesticks(
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

    # --- 3. 组装接口 Record (遵循 NamedTuple 规约) ---
    return Broker(
        get_watchlist_by_group=get_watchlist_by_group,
        get_watchlist=get_watchlist,
        get_holdings=get_holdings,
        get_watchlist_groups=get_watchlist_groups,
        get_stock_static_info=get_stock_static_info,
        get_account_balance=get_account_balance,
        get_history_candlesticks=get_history_candlesticks,
    )


__all__ = ["create_longbridge_broker"]