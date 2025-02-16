from markets.IMarket import IMarket


class HKMarket(IMarket):
    """港股市场"""

    def get_trading_hours(self):
        print("HKMarket: Getting trading hours...")
