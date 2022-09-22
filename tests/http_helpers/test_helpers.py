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
            FilterParams(market="10000", max=250, start_ts=1450000, end_ts=1460000),
        )
        self.assertIsNotNone(url)
        self.assertEqual(
            url, "http://tracker?market=10000&max=250&startTs=1450000&endTs=1460000"
        )
