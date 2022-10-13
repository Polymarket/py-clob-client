from unittest import TestCase
from py_clob_client.clob_types import FilterParams

from py_clob_client.http_helpers.helpers import build_query_params, add_query_params


class TestHelpers(TestCase):
    def test_build_query_params(self):
        # last is ?
        url = build_query_params("http://tracker?", "q1", "a")
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?q1=a")

        # last is not ?
        url = build_query_params("http://tracker?q1=a", "q2", "b")
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?q1=a&q2=b")

    def test_add_query_params(self):
        url = add_query_params(
            "http://tracker",
            FilterParams(market="10000", limit=250, after=1450000, before=1460000),
        )
        self.assertIsNotNone(url)
        self.assertEqual(
            url, "http://tracker?market=10000&limit=250&after=1450000&before=1460000"
        )
