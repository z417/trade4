from brokers.longport import LongportBroker
from services.quote_service import QuoteService
from markets.hk_market import HKMarket


def main():
    # 初始化券商
    broker = LongportBroker(".env")
    hkmarket = HKMarket()

    # 初始化服务
    qs = QuoteService(broker, hkmarket)

    # print(qs.watchlistGroups)
    print(qs.holdings)
    # print(qs.get_watchlist_by_group("options"))
    # 查询股票信息
    # stock_info = qs.get_stock_info("600519")
    # print(stock_info)
    # print(qs.pull_quote(["02438.HK"]))
    # print(qs.pull_depth("700.HK"))
    print(qs.pull_intraday("TSLA.US")[0])


if __name__ == "__main__":
    main()
