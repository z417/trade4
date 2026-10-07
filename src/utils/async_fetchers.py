import asyncio
import math
import re
import json
import random
from typing import Literal, Any
import httpx
import pandas as pd

# 模块级常量配置
EASTMONEY_HEADERS = {
    "Host": "push2.eastmoney.com",
    "Referer": "https://quote.eastmoney.com/center/gridlist.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

SINA_HEADERS = {
    "Referer": "https://finance.sina.com.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


async def _safe_fetch_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict[str, Any],
    headers: dict[str, str],
    semaphore: asyncio.Semaphore,
    jitter_range: tuple[float, float] = (0.2, 1.0),
) -> dict[str, Any]:
    """带有信号量限流和随机抖动的安全请求包装器"""
    async with semaphore:
        # 非阻塞的随机休眠，防反爬
        await asyncio.sleep(random.uniform(*jitter_range))
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        response.raise_for_status()
        return response.json()


async def fetch_stock_from_eastmoney_async(ex: Literal["SSE", "SZSE", "HKEX", "US"]) -> pd.DataFrame:
    """全异步拉取东方财富标的 (带并发控制)"""
    filter_str = {
        "SSE": {"A-shares": "m:0+t:6+f:!2,m:0+t:80+f:!2", "ChiNext": "m:0+t:80+f:!2"},
        "SZSE": {"A-shares": "m:1+t:2+f:!2,m:1+t:23+f:!2", "STAR": "m:1+t:23+f:!2"},
        "HKEX": {"Main": "m:128+t:3", "GEM": "m:128+t:4"},
        "US": {"All": "m:105,m:106,m:107"},
    }

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    fields = "f12,f14"
    semaphore = asyncio.Semaphore(2)  # 最高允许 2 个并发请求
    all_dfs: list[pd.DataFrame] = []

    # 复用连接池
    async with httpx.AsyncClient() as client:
        for board, fs in filter_str.get(ex, {}).items():
            base_params = {"np": 0, "fs": fs, "fields": fields, "pz": 100}

            # 1. 先拉取第一页获取总数
            first_page_data = await _safe_fetch_json(client, url, base_params | {"pn": 1}, EASTMONEY_HEADERS, semaphore)
            total = first_page_data.get("data", {}).get("total", 0) if first_page_data.get("data") else 0

            if total == 0:
                continue

            total_pages = math.ceil(total / 100)

            # 2. 组装剩余页码的并发任务
            tasks = [
                _safe_fetch_json(client, url, base_params | {"pn": pn}, EASTMONEY_HEADERS, semaphore)
                for pn in range(1, total_pages + 1)
            ]

            # 3. 兵分多路，异步等待全部完成 (gather 会保持顺序，但底层是并发执行的)
            results = await asyncio.gather(*tasks, return_exceptions=True)

            tmp_list = []
            for res in results:
                if isinstance(res, Exception):
                    print(f"Eastmoney Fetch Error: {res}")  # 现实中这里应该接入 logging
                    continue
                diff = res.get("data", {}).get("diff", [])
                tmp_list.extend(list(diff.values()) if isinstance(diff, dict) else diff)

            if tmp_list:
                all_dfs.append(pd.DataFrame(tmp_list).assign(board=board))

    if not all_dfs:
        return pd.DataFrame()

    # 为了防止巨大的 DataFrame 拼接卡住事件循环，将其扔进纯计算线程
    final_df = await asyncio.to_thread(pd.concat, all_dfs, ignore_index=True)
    return final_df.rename(columns={"f12": "code", "f14": "name"})


async def fetch_stock_from_sina_async(ex: Literal["US"]) -> pd.DataFrame:
    """全异步拉取新浪美股标的 (带并发控制)"""
    url = "https://stock.finance.sina.com.cn/usstock/api/jsonp.php/jQuery/US_CategoryService.getList"
    semaphore = asyncio.Semaphore(3)  # 新浪比较严，并发降到 3
    all_dfs: list[pd.DataFrame] = []

    async def _fetch_sina_page(client: httpx.AsyncClient, pn: int) -> dict[str, Any]:
        async with semaphore:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            resp = await client.get(
                url, params={"page": pn, "num": 60, "sort": "mktcap", "asc": 0}, headers=SINA_HEADERS, timeout=15.0
            )
            resp.raise_for_status()
            match = re.search(r"jQuery\(([\s\S]*)\)", resp.text)
            return json.loads(match.group(1)) if match else {}

    async with httpx.AsyncClient() as client:
        # 1. 获取第一页及总数
        first_page = await _fetch_sina_page(client, 1)
        total = int(first_page.get("count", 0))

        if total > 0:
            total_pages = math.ceil(total / 60)

            # 2. 并发组装
            tasks = [_fetch_sina_page(client, pn) for pn in range(1, total_pages + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            tmp_list = []
            for res in results:
                if isinstance(res, Exception):
                    continue
                tmp_list.extend(res.get("data", []))

            if tmp_list:
                all_dfs.append(pd.DataFrame(tmp_list).assign(board="All"))

    if not all_dfs:
        return pd.DataFrame()

    final_df = await asyncio.to_thread(pd.concat, all_dfs, ignore_index=True)
    return final_df[["cname", "symbol", "market"]].rename(
        columns={"symbol": "code", "cname": "name", "market": "board"}
    )
