import math
import re
import json
import requests
import pandas as pd
from multiprocessing.dummy import Pool
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Literal


T = TypeVar("T")
R = TypeVar("R")


class Market(ABC, Generic[T, R]):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Market, cls).__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def spa_stock_info(self):
        pass

    @classmethod
    def fetch_stock_from_eastmoney(
        cls, ex: Literal["SSE", "SZSE", "HKEX", "US"]
    ) -> pd.DataFrame:
        """
        东方财富网
        https://quote.eastmoney.com/center/qqzs.html
        """
        filter_str = {
            "SSE": {  # 上海
                "A-shares": "m:0+t:6+f:!2,m:0+t:80+f:!2",  # A股
                "ChiNext": "m:0+t:80+f:!2",  # 科创板
            },
            "SZSE": {  # 深圳
                "A-shares": "m:1+t:2+f:!2,m:1+t:23+f:!2",
                "STAR": "m:1+t:23+f:!2",  # 创业板
            },
            "HKEX": {  # 香港
                "Main": "m:128+t:3",  # 主板
                "GEM": "m:128+t:4",  # 创业板
            },
            "BSE": {"A-shares": "m:0+t:81+s:262144+f:!2"},  # 北京
            "US": {"All": "m:105,m:106,m:107"},
        }
        fields = "f12,f14"  # "code,name"
        stk_df = pd.DataFrame()

        def in_call(fs, fields, page_num=1, page_size=100):
            try:
                return requests.get(  # 使用 requests.get，避免 Session 线程安全问题
                    "https://push2.eastmoney.com/api/qt/clist/get",
                    timeout=15,
                    headers={
                        "Host": "push2.eastmoney.com",
                        "Referer": "https://quote.eastmoney.com/center/gridlist.html",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                    },
                    params={
                        "np": 0,  # 是否返回非交易品种(如 ST 股、退市股等): 1:包含, 0:不包含
                        "fs": fs,  # 筛选条件(Filter String)
                        "fields": fields,  # 返回字段
                        "pn": page_num,
                        "pz": page_size,  # 最大支持100条
                    },
                ).json()
            except requests.RequestException as e:
                import sys

                print(e)
                sys.exit(1)

        for board, fs in filter_str.get(ex, {}).items():
            data = in_call(fs, fields, 1, 1)
            total = data["data"]["total"] if data.get("data") else 0
            if total == 0:
                continue
            total_pages = math.ceil(total / 100)
            tasks = [(fs, fields, pn) for pn in range(1, total_pages + 1)]
            with Pool(processes=4) as p:
                results = p.map(
                    lambda args: in_call(args[0], args[1], args[2])
                    .get("data", {})
                    .get("diff", []),
                    tasks,
                )
            tmp_list = []
            for diff in results:
                if isinstance(diff, dict):
                    diff = list(diff.values())
                tmp_list.extend(diff)
            stk_df = pd.concat(
                [stk_df, pd.DataFrame(tmp_list).assign(board=board)],
                ignore_index=True,
            )
        return stk_df.rename(
            columns={
                "f12": "code",
                "f14": "name",
            }
        )

    @classmethod
    def fetch_stock_from_sina(
        cls, ex: Literal["SSE", "SZSE", "HKEX", "US"]
    ) -> pd.DataFrame:
        filter_str = {
            "US": {
                "url": "https://stock.finance.sina.com.cn/usstock/api/jsonp.php/jQuery/US_CategoryService.getList"
            },
        }
        stk_df = pd.DataFrame()

        def in_call(fs, page_num=1, page_size=60):
            try:
                jsonp_str = requests.get(  # 使用 requests.get，避免 Session 线程安全问题
                    f"{fs}",
                    timeout=15,
                    headers={
                        "Referer": "https://finance.sina.com.cn/",
                        "sec-ch-ua-platform": "Windows",
                        "sec-fetch-dest": "script",
                        "sec-fetch-mode": "no-cors",
                        "sec-fetch-site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                    },
                    params={
                        "page": page_num,
                        "num": page_size,
                        "sort": "mktcap",
                        "asc": 0,
                        "market": None,
                        "id": None,
                    },
                ).text
                match = re.search(r"jQuery\((\{.*\})\)", jsonp_str, re.DOTALL)
            except requests.RequestException as e:
                import sys

                print(e)
                sys.exit(1)

            return json.loads(match.group(1)) if match else {}

        for board, fs in filter_str.get(ex, {}).items():
            data = in_call(fs, 1, 1)
            total = int(data["count"]) if data else 0
            if total == 0:
                continue
            total_pages = math.ceil(total / 60)
            tasks = [(fs, pn) for pn in range(1, total_pages + 1)]
            with Pool(processes=4) as p:
                results = p.map(
                    lambda args: in_call(args[0], args[1]).get("data", {}),
                    tasks,
                )
            tmp_list = []
            for diff in results:
                tmp_list.extend(diff)
            stk_df = pd.concat(
                [stk_df, pd.DataFrame(tmp_list).assign(board=board)],
                ignore_index=True,
            )
        return stk_df[["cname", "symbol", "market"]].rename(
            columns={
                "symbol": "code",
                "cname": "name",
                "market": "board",
            }
        )

    @property
    @abstractmethod
    def trading_hours(self) -> R:
        pass

    @property
    @abstractmethod
    def security_list(self) -> pd.DataFrame:
        pass


__all__ = ["Market"]
