from core.market import Market


class HKMarket(Market):
    """港股市场"""

    def get_trading_hours(self):
        print("HKMarket: Getting trading hours...")
