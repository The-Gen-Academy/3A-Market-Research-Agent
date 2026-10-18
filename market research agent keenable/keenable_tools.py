from langchain_core.tools import tool

from keenable_client import KeenableClient

_client = None


def _get_client() -> KeenableClient:
    global _client
    if _client is None:
        _client = KeenableClient()
    return _client


def _format_results(results: list[dict]) -> str:
    if not results:
        return "No results found."

    formatted = []
    for result in results:
        published = result.get("published_date")
        date_line = f"\n  Published: {published}" if published else ""
        formatted.append(
            f"- {result['title']}\n  {result.get('snippet', '')}"
            f"{date_line}\n  Source: {result['url']}"
        )
    return "\n".join(formatted)


@tool
def keenable_web_search(query: str) -> str:
    """Search the web via Keenable for pricing, features, and market positioning."""
    return _format_results(_get_client().search_web(query))


@tool
def keenable_news_search(query: str) -> str:
    """Search via Keenable for recent launches and announcements."""
    return _format_results(_get_client().search_news(query))
