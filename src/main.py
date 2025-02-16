from brokers.longport import LongportBroker
from services.quote_service import QuoteService
from markets.hk_market import HKMarket


def main():
    # 初始化券商
    broker = LongportBroker(".env")
    hkmarket = HKMarket()

    # 初始化服务
    quote_service = QuoteService(broker, hkmarket)

    print(quote_service.get_watchlist().__len__())
    # 查询股票信息
    # stock_info = quote_service.get_stock_info("600519")
    # print(stock_info)


if __name__ == "__main__":
    main()
