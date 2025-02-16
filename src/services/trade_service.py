class TradeService:
    def __init__(self, trade_provider):
        self.trade_provider = trade_provider

    def place_order(self, stock_code: str, amount: int, price: float) -> bool:
        return self.trade_provider.place_order(stock_code, amount, price)
