from unittest import TestCase
from py_clob_client.clob_types import (
    TradeParams,
    OpenOrderParams,
    DropNotificationParams,
    BalanceAllowanceParams,
    AssetType,
    OrderScoringParams,
    OrdersScoringParams,
)

from py_clob_client.http_helpers.helpers import (
    build_query_params,
    add_query_trade_params,
    add_query_open_orders_params,
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

    def test_add_query_trade_params(self):
        url = add_query_trade_params(
            "http://tracker",
            TradeParams(
                market="10000",
                after=1450000,
                before=1460000,
                asset_id="100",
                maker_address="0x0",
                id="aa-bb",
            ),
            next_cursor="AA==",
        )
        self.assertIsNotNone(url)
        self.assertEqual(
            url,
            "http://tracker?market=10000&asset_id=100&after=1450000&before=1460000&maker_address=0x0&id=aa-bb&next_cursor=AA==",
        )

    def test_add_query_open_orders_params(self):
        url = add_query_open_orders_params(
            "http://tracker",
            OpenOrderParams(market="10000", asset_id="100", id="aa-bb"),
        )
        self.assertIsNotNone(url)
        self.assertEqual(
            url,
            "http://tracker?market=10000&asset_id=100&id=aa-bb&next_cursor=MA==",
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
            BalanceAllowanceParams(asset_type=AssetType.COLLATERAL, signature_type=0),
        )
        self.assertIsNotNone(url)
        self.assertEqual(url, "http://tracker?asset_type=COLLATERAL&signature_type=0")

        url = add_balance_allowance_params_to_url(
            "http://tracker",
            BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL, token_id="222", signature_type=1
            ),
        )
        self.assertIsNotNone(url)
        self.assertEqual(
            url, "http://tracker?asset_type=CONDITIONAL&token_id=222&signature_type=1"
        )

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
