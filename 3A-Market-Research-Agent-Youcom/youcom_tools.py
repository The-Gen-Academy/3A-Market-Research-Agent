from langchain_core.tools import tool

from youcom_client import YouComClient

_client = None


def _get_client() -> YouComClient:
    global _client
    if _client is None:
        _client = YouComClient()
    return _client


def _format_results(results: list[dict]) -> str:
    if not results:
        return "No results found."
    return "\n".join(
        f"- {r['title']}\n  {r.get('snippet', '')}\n  Source: {r['url']}"
        for r in results
    )


@tool
def youcom_web_search(query: str) -> str:
    """Search the web via you.com for pricing, features, and market positioning."""
    return _format_results(_get_client().search_web(query))


@tool
def youcom_news_search(query: str) -> str:
    """Search recent news via you.com for launches and announcements."""
    return _format_results(_get_client().search_news(query))
