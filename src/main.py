from dotenv import dotenv_values

from brokers import BrokerLongport
from services import QuoteService, TradeService
from markets import CNMarket, HKMarket, USMarket


def main():
    # get config from .env
    conf = dotenv_values(".env")

    # 初始化券商
    broker = BrokerLongport(conf).connect()

    cnmarket = CNMarket(conf)
    hkmarket = HKMarket(conf)
    usmarket = USMarket(conf)

    # 初始化服务
    quote_service = QuoteService(broker, usmarket)
    trade_service = TradeService(broker, cnmarket)

    quote_service.test()


if __name__ == "__main__":
    main()
