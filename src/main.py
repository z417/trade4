from dotenv import dotenv_values

from config import get_config, Config
from brokers import BrokerLongport
from services import QuoteService, TradeService
from markets import CNMarket, HKMarket, USMarket


def main():
    # get config from .env
    conf: Config = get_config()

    # 初始化券商
    broker = BrokerLongport(conf).connect()

    cnmarket = CNMarket(conf)
    hkmarket = HKMarket(conf)
    usmarket = USMarket(conf)

    # 初始化服务
    quote_service = QuoteService(broker, usmarket)
    trade_service = TradeService(broker, usmarket)

    quote_service.test()


if __name__ == "__main__":
    main()
