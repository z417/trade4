from config import get_config, Config
from brokers import BrokerLongport
from services import QuoteService, TradeService
from markets import CNMarket, HKMarket, USMarket


def main():
    # 获取全局配置
    conf: Config = get_config()

    # 初始化券商 (长桥)
    broker = BrokerLongport(conf).connect()

    # 初始化市场
    cnmarket = CNMarket(conf)
    hkmarket = HKMarket(conf)
    usmarket = USMarket(conf)

    # 注入券商与 A 股市场到服务中
    quote_service = QuoteService(broker, cnmarket)
    trade_service = TradeService(broker, cnmarket)

    # 执行大 A 股票入库 -> EPS 筛选 -> 历史日 K 线获取流程
    quote_service.test()


if __name__ == "__main__":
    main()
