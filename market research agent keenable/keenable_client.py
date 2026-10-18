import os

from keenable import Keenable


class KeenableClient:
    """Adapter around Keenable Search for normalized web results."""

    def __init__(self, api_key: str | None = None):
        # Keenable supports keyless search. Supplying a key raises the public
        # hourly rate limit, but it is deliberately optional here.
        self.client = Keenable(
            api_key=api_key or os.getenv("KEENABLE_API_KEY"),
            client_source="3A Market Research Agent",
        )

    @staticmethod
    def _normalize(result) -> dict:
        return {
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet,
            "published_date": result.published_at or "",
        }

    def _search(self, query: str, num_results: int) -> list[dict]:
        response = self.client.search(query, mode="pro")
        return [self._normalize(result) for result in response][:num_results]

    def search_web(self, query: str, num_results: int = 5) -> list[dict]:
        return self._search(query, num_results)

    def search_news(self, query: str, num_results: int = 5) -> list[dict]:
        # Keenable uses one semantic web index rather than a separate news
        # topic, so the caller's launch/announcement query supplies the intent.
        return self._search(query, num_results)
