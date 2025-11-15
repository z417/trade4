from dataclasses import field

symbol = field(
    metadata={
        "desc": "标的代码",
        "description": "标的代码，使用 ticker.region 格式，例如：700.HK",
        "pattern": r"^[A-Z0-9]{1,10}\.(HK|US|SH|SZ)$",
        "priority": 1,
    },
)
market = field(metadata={"desc": "市场"})
name_cn = field(metadata={"desc": "标的名称", "priority": 0})
group_id = field(metadata={"desc": "分组号", "priority": 0})
group_name = field(metadata={"desc": "组名", "priority": 0})
exchange = field(metadata={"desc": "交易所"})
currency = field(metadata={"desc": "货币"})
eps = field(metadata={"desc": "每股收益(静)", "priority": 1})
eps_ttm = field(metadata={"desc": "每股收益(TTM)", "priority": 1})
bps = field(metadata={"desc": "每股净资产", "priority": 1})
dividend_yield = field(metadata={"desc": "股息率", "priority": 1})
stock_derivatives = field(metadata={"desc": "衍生品类型"})
board = field(metadata={"desc": "所属板块"})

__all__ = [
    "symbol",
    "market",
    "name_cn",
    "group_id",
    "group_name",
    "exchange",
    "currency",
    "eps",
    "eps_ttm",
    "bps",
    "dividend_yield",
    "stock_derivatives",
    "board",
]
