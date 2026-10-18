import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from keenable_client import KeenableClient


class SearchAdapterTests(unittest.TestCase):
    def test_keenable_is_keyless_and_normalizes_results(self):
        result = SimpleNamespace(
            title="Example",
            url="https://example.com",
            snippet="Useful text",
            published_at="2026-10-01",
        )
        sdk = SimpleNamespace(search=lambda *args, **kwargs: [result])

        with patch("keenable_client.Keenable", return_value=sdk) as constructor:
            with patch.dict(os.environ, {}, clear=True):
                client = KeenableClient()
                results = client.search_web("query")

        constructor.assert_called_once_with(
            api_key=None,
            client_source="3A Market Research Agent",
        )
        self.assertEqual(
            results,
            [{
                "title": "Example",
                "url": "https://example.com",
                "snippet": "Useful text",
                "published_date": "2026-10-01",
            }],
        )

if __name__ == "__main__":
    unittest.main()
