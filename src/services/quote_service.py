from typing import List, Optional
from decimal import Decimal
import pandas as pd
import pandas_ta as ta
from core import Broker, Market, DatabaseService, SecurityStaticInfoModel
from utils import async_timer_scope, logger


class QuoteService:
    """行情与选股服务 (业务逻辑层 - 全异步与协议驱动)"""

    def __init__(self, broker: Broker, market: Market, db: Optional[DatabaseService] = None):
        self.broker: Broker = broker
        self.market: Market = market
        self.db: Optional[DatabaseService] = db

    async def sync_market_securities(self) -> int:
        """
        同步市场股票列表并入库 DuckDB

        :return: 入库股票总数量
        """
        table_name = await self.market.spa_stock_info()
        sec_df = await self.market.get_security_list()
        total_count = sec_df.shape[0]
        logger.info(f"[QuoteService] 成功同步标的至 {table_name}，当前可用标的共 {total_count} 只。")
        return total_count

    async def get_securities(self) -> pd.DataFrame:
        """获取当前市场所有标的列表"""
        return await self.market.get_security_list()

    async def filter_stocks_by_indicators(
        self,
        symbols: Optional[List[str]] = None,
        min_eps: Optional[Decimal] = None,
        min_bps: Optional[Decimal] = None,
        min_dividend_yield: Optional[Decimal] = None,
        top_n: Optional[int] = None,
        save_to_db: bool = True,
    ) -> List[SecurityStaticInfoModel]:
        """
        根据 EPS、BPS、股息率等财务指标筛选股票

        :param symbols: 待筛选标的列表，若为 None 则默认取当前市场全部标的
        :param min_eps: 最低每股收益 (EPS)
        :param min_bps: 最低每股净资产 (BPS)
        :param min_dividend_yield: 最低股息率
        :param top_n: 返回前 N 个标的
        :param save_to_db: 是否将筛选结果持久化至 DuckDB 表 STOCK_SCREEN_RESULT
        :return: 满足条件的标的静态信息列表
        """
        if symbols is None:
            sec_df = await self.get_securities()
            if sec_df.empty:
                logger.info("[QuoteService] 本地暂无标的列表，正在执行同步...")
                await self.sync_market_securities()
                sec_df = await self.get_securities()
            symbols = sec_df["symbol"].dropna().tolist()

        logger.info(f"[QuoteService] 开始批量获取 {len(symbols)} 只标的的静态财务指标...")
        async with async_timer_scope("[QuoteService] 标的静态指标拉取", logger.info):
            static_infos = await self.broker.get_stock_static_info(symbols)

        filtered: List[SecurityStaticInfoModel] = []
        for info in static_infos:
            if min_eps is not None and (info.eps is None or info.eps < min_eps):
                continue
            if min_bps is not None and (info.bps is None or info.bps < min_bps):
                continue
            if min_dividend_yield is not None and (
                info.dividend_yield is None or info.dividend_yield < min_dividend_yield
            ):
                continue
            filtered.append(info)

        # 默认按 EPS 降序排列 (Decimal 精度比较)
        filtered.sort(key=lambda x: x.eps if x.eps is not None else Decimal("-999999"), reverse=True)

        if top_n is not None and top_n > 0:
            filtered = filtered[:top_n]

        logger.info(f"[QuoteService] 筛选完成，符合条件标的共 {len(filtered)} 只。")

        if save_to_db and filtered and self.db is not None:
            records = [
                {
                    "symbol": item.symbol,
                    "name": item.name,
                    "exchange": item.exchange,
                    "eps": float(item.eps) if item.eps is not None else None,
                    "eps_ttm": float(item.eps_ttm) if item.eps_ttm is not None else None,
                    "bps": float(item.bps) if item.bps is not None else None,
                    "dividend_yield": (
                        float(item.dividend_yield) if item.dividend_yield is not None else None
                    ),
                    "total_shares": item.total_shares,
                    "circulating_shares": item.circulating_shares,
                }
                for item in filtered
            ]
            result_df = pd.DataFrame(records)
            await self.db.insert_df("STOCK_SCREEN_RESULT", result_df, if_exists="replace")
            logger.info("[QuoteService] 筛选结果已持久化至 DuckDB 表 STOCK_SCREEN_RESULT。")

        return filtered

    async def get_history_candlesticks(
        self, symbol: str, count: int = 100, calculate_indicators: bool = True
    ) -> pd.DataFrame:
        """
        获取指定标的的历史日K线（前复权），并支持计算技术指标

        :param symbol: 标的代码，长桥格式（如 '000001.SZ'）
        :param count: 获取K线数量，默认100根
        :param calculate_indicators: 是否使用 pandas-ta 计算均线等指标
        :return: 包含行情与指标的 DataFrame
        """
        df = await self.broker.get_history_candlesticks(symbol=symbol, count=count)
        if df.empty:
            logger.warning(f"[QuoteService] 未获取到标的 {symbol} 的日K线数据。")
            return df

        if calculate_indicators and len(df) >= 5:
            close_series = df["close"].astype(float)
            df["ma5"] = ta.sma(close_series, length=5)
            if len(df) >= 20:
                df["ma20"] = ta.sma(close_series, length=20)

        return df

    async def test(self) -> None:
        """测试业务流程：股票入库 -> EPS筛选 -> 历史日K线获取"""
        print("\n===== 步骤 0: 完善大 A 股票入库 =====")
        await self.sync_market_securities()
        securities = await self.get_securities()
        print(f"当前数据库中的标的样例（前5条）:")
        if not securities.empty:
            cols = [c for c in ["symbol", "exchange", "code", "name", "board"] if c in securities.columns]
            print(securities.head(5)[cols])

        print("\n===== 步骤 1: 遍历大 A 股票按 EPS 筛选优质标的 =====")
        sample_symbols = securities["symbol"].head(100).tolist() if not securities.empty else ["000001.SZ"]
        screened = await self.filter_stocks_by_indicators(
            symbols=sample_symbols,
            min_eps=Decimal("0.50"),
            top_n=5,
        )
        for i, item in enumerate(screened, 1):
            print(f"[{i}] {item.symbol} ({item.name}): EPS={item.eps}, BPS={item.bps}, 股息率={item.dividend_yield}")

        print("\n===== 步骤 2: 获取标的历史日 K 线 =====")
        target_symbol = screened[0].symbol if screened else "000001.SZ"
        print(f"正在获取标的 {target_symbol} 的历史日K线数据...")
        kline_df = await self.get_history_candlesticks(target_symbol, count=30)
        print(f"获取到 {len(kline_df)} 条日K线数据，最近3日行情:")
        display_cols = [c for c in ["date", "symbol", "close", "volume", "ma5", "ma20"] if c in kline_df.columns]
        if not kline_df.empty:
            print(kline_df.tail(3)[display_cols])


__all__ = ["QuoteService"]
