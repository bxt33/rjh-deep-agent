from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: float


class TavilySearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        print(f"[TavilySearch] 搜索：{query}")

        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }

        request = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as err:
            print(f"[TavilySearch] 搜索失败：{err}")
            return []

        results = [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", "")[:800],
                score=float(item.get("score", 0)),
            )
            for item in data.get("results", [])
        ]

        print(f"[TavilySearch] 获取到 {len(results)} 条结果")
        return results
