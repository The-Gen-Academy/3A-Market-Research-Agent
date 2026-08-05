import os
import httpx

YOUCOM_BASE_URL = "https://ydc-index.io"


class YouComClient:
    """Thin wrapper around the you.com Search API (a single endpoint returns both web and news results)."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YOUCOM_API_KEY")
        if not self.api_key:
            raise ValueError("YOUCOM_API_KEY not found in environment.")
        self.headers = {"X-API-Key": self.api_key}

    def _search(self, query: str, count: int) -> dict:
        response = httpx.get(
            f"{YOUCOM_BASE_URL}/v1/search",
            params={"query": query, "count": count},
            headers=self.headers,
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json().get("results", {})

    def search_web(self, query: str, num_results: int = 5) -> list[dict]:
        results = self._search(query, num_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": " ".join(r.get("snippets", [])) or r.get("description", ""),
            }
            for r in results.get("web", [])[:num_results]
        ]

    def search_news(self, query: str, num_results: int = 5) -> list[dict]:
        results = self._search(query, num_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("description", ""),
                "age": r.get("page_age", ""),
            }
            for r in results.get("news", [])[:num_results]
        ]
