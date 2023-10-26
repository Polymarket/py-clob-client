from unittest import TestCase
from py_clob_client.model.clob import (
    FilterParams,
    DropNotificationParams,
    BalanceAllowanceParams,
    AssetType,
    OrderScoringParams,
    OrdersScoringParams,
)

from py_clob_client.http_helpers.helpers import (
    build_query_params,
    add_query_params,
    drop_notifications_query_params,
    add_balance_allowance_params_to_url,
    add_order_scoring_params_to_url,
    add_orders_scoring_params_to_url,
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

    def test_drop_notifications_query_params(self):
        url = drop_notifications_query_params(
            "http://tracker",
            DropNotificationParams(ids=["1", "2", "3"]),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?ids=1,2,3")

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

    def test_add_order_scoring_params_to_url(self):
        url = add_order_scoring_params_to_url(
            "http://tracker",
            OrderScoringParams(orderId="0x0123abc"),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?order_id=0x0123abc")

    def test_add_orders_scoring_params_to_urll(self):
        url = add_orders_scoring_params_to_url(
            "http://tracker",
            OrdersScoringParams(orderIds=["0x0", "0x1", "0x2"]),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?order_ids=0x0,0x1,0x2")
