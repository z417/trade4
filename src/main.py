import asyncio
from config import get_config, Config
from brokers import create_longbridge_broker
from services import QuoteService, TradeService, create_duckdb_service
from markets import CNMarket, HKMarket, USMarket
from utils import setup_logger, logger


async def async_main():
    setup_logger()
    logger.info("正在启动 trade4 量化交易系统...")

    # 获取全局配置
    conf: Config = get_config()

    # 初始化数据库服务 (DuckDB)
    db = await create_duckdb_service(conf.database_path)

    try:
        # 初始化券商 (长桥 Longbridge OpenAPI)
        broker = await create_longbridge_broker()

        # 初始化市场 (FP-First 闭包工厂)
        cnmarket = CNMarket(conf, db)
        hkmarket = HKMarket(conf, db)
        usmarket = USMarket(conf, db)

        # 依赖注入：注入券商、市场与存储至业务服务
        quote_service = QuoteService(broker, cnmarket, db)
        trade_service = TradeService(broker, cnmarket)

        # 执行大 A 股票入库 -> EPS 筛选 -> 历史日 K 线获取流程
        await quote_service.test()
    finally:
        await db.close()


def main():
    """CLI 同步入口"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
