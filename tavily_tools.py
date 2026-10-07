from langchain_core.tools import tool

from tavily_client import TavilyClient

_client = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient()
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
def tavily_web_search(query: str) -> str:
    """Search the web via Tavily for pricing, features, and market positioning."""
    return _format_results(_get_client().search_web(query))


@tool
def tavily_news_search(query: str) -> str:
    """Search recent news via Tavily for launches and announcements."""
    return _format_results(_get_client().search_news(query))
