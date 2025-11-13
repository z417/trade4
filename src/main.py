from brokers.broker_longport import BrokerLongport
from services import QuoteService, TradeService
from markets.hk_market import HKMarket


def main():
    # 初始化券商
    broker = BrokerLongport(".env").connect()
    hkmarket = HKMarket()

    # 初始化服务
    quote_service = QuoteService(broker, hkmarket)
    trade_service = TradeService(broker, hkmarket)

    quote_service.test()


if __name__ == "__main__":
    main()
