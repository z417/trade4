from IMarket import IMarket


class USMarket(IMarket):
    """美股市场"""

    def get_trading_hours(self):
        print("USMarket: Getting trading hours...")
