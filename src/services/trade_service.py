from core import Broker, Market


class TradeService:
    def __init__(self, broker, market):
        self.broker: Broker = broker
        self.market: Market = market

    def test(self):
        print(self.broker.account_balance)
