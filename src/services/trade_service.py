from core.broker import Broker
from core.market import Market


class TradeService:
    def __init__(self, broker, market):
        self.broker: Broker = broker
        self.market: Market = market

    def test(self):
        print(self.broker.get_account_balance())
