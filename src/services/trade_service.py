from core import Broker, Market


class TradeService:
    """交易与市场业务服务"""

    def __init__(self, broker: Broker, market: Market) -> None:
        self.broker: Broker = broker
        self.market: Market = market

    async def test(self) -> None:
        """获取账户余额测试"""
        balance = await self.broker.get_account_balance()
        print(balance)


__all__ = ["TradeService"]
