import os

from tavily import TavilyClient as TavilySDKClient


class TavilyClient:
    """Small adapter around Tavily Search for normalized web and news results."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment.")
        self.client = TavilySDKClient(api_key=self.api_key)

    def _search(self, query: str, topic: str, num_results: int) -> list[dict]:
        response = self.client.search(
            query=query,
            topic=topic,
            search_depth="advanced",
            max_results=num_results,
            include_answer=False,
            include_raw_content=False,
        )
        return response.get("results", [])

    @staticmethod
    def _normalize(result: dict) -> dict:
        return {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("content", ""),
            "published_date": result.get("published_date", ""),
        }

    def search_web(self, query: str, num_results: int = 5) -> list[dict]:
        return [
            self._normalize(result)
            for result in self._search(query, "general", num_results)
        ]

    def search_news(self, query: str, num_results: int = 5) -> list[dict]:
        return [
            self._normalize(result)
            for result in self._search(query, "news", num_results)
        ]
