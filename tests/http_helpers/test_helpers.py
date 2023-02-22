from unittest import TestCase
from py_clob_client.clob_types import (
    FilterParams,
    TradeNotificationParams,
    BalanceAllowanceParams,
    AssetType,
)

from py_clob_client.http_helpers.helpers import (
    build_query_params,
    add_query_params,
    add_trade_notifications_query_params,
    add_balance_allowance_params_to_url,
)


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

    def test_add_trade_notifications_query_params(self):
        url = add_trade_notifications_query_params(
            "http://tracker",
            TradeNotificationParams(index=12345),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?index=12345")

    def test_add_balance_allowance_params_to_url(self):
        url = add_balance_allowance_params_to_url(
            "http://tracker",
            BalanceAllowanceParams(asset_type=AssetType.COLLATERAL),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?asset_type=COLLATERAL")

        url = add_balance_allowance_params_to_url(
            "http://tracker",
            BalanceAllowanceParams(asset_type=AssetType.CONDITIONAL, token_id="222"),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?asset_type=CONDITIONAL&token_id=222")
