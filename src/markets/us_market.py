from core.market import Market


class USMarket(Market):
    """美股市场"""

    def get_trading_hours(self):
        print("USMarket: Getting trading hours...")
