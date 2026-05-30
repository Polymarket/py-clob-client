from unittest import TestCase
from unittest.mock import MagicMock, patch


ORDER_ID = "0xabc123"
FULL_ORDER = {
    "id": ORDER_ID,
    "status": "CANCELED",
    "side": "BUY",
    "original_size": "100000000",
    "size_matched": "30000000",
    "price": "0.5",
    "asset_id": "52114319501245915516055106046884209969926127482827954674443846427813813222426",
}


def _make_client():
    """Return a ClobClient with auth mocked out."""
    from py_clob_client.client import ClobClient

    client = ClobClient.__new__(ClobClient)
    client.host = "https://clob.polymarket.com"
    client.signer = MagicMock()
    client.creds = MagicMock()
    client.assert_level_2_auth = MagicMock()
    return client


class TestCancel(TestCase):
    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_returns_full_order_on_success(self, mock_delete, _mock_headers):
        mock_delete.return_value = {"canceled": [ORDER_ID], "not_canceled": {}}
        client = _make_client()
        client.get_order = MagicMock(return_value=FULL_ORDER)

        result = client.cancel(ORDER_ID)

        client.get_order.assert_called_once_with(ORDER_ID)
        self.assertEqual(result, FULL_ORDER)
        self.assertIn("size_matched", result)

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_returns_raw_response_when_not_canceled(self, mock_delete, _mock_headers):
        raw = {"canceled": [], "not_canceled": {ORDER_ID: "Order not found"}}
        mock_delete.return_value = raw
        client = _make_client()
        client.get_order = MagicMock()

        result = client.cancel(ORDER_ID)

        client.get_order.assert_not_called()
        self.assertEqual(result, raw)

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_returns_raw_response_when_get_order_fails(self, mock_delete, _mock_headers):
        raw = {"canceled": [ORDER_ID], "not_canceled": {}}
        mock_delete.return_value = raw
        client = _make_client()
        client.get_order = MagicMock(side_effect=Exception("network error"))

        result = client.cancel(ORDER_ID)

        self.assertEqual(result, raw)


class TestCancelOrders(TestCase):
    ORDER_ID_2 = "0xdef456"

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_orders_returns_full_order_objects(self, mock_delete, _mock_headers):
        mock_delete.return_value = {
            "canceled": [ORDER_ID],
            "not_canceled": {},
        }
        client = _make_client()
        client.get_order = MagicMock(return_value=FULL_ORDER)

        result = client.cancel_orders([ORDER_ID])

        self.assertIn("canceled", result)
        self.assertIn("not_canceled", result)
        self.assertEqual(len(result["canceled"]), 1)
        self.assertEqual(result["canceled"][0], FULL_ORDER)
        self.assertIn("size_matched", result["canceled"][0])

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_orders_preserves_not_canceled(self, mock_delete, _mock_headers):
        mock_delete.return_value = {
            "canceled": [ORDER_ID],
            "not_canceled": {self.ORDER_ID_2: "Order already matched"},
        }
        client = _make_client()
        client.get_order = MagicMock(return_value=FULL_ORDER)

        result = client.cancel_orders([ORDER_ID, self.ORDER_ID_2])

        self.assertEqual(result["not_canceled"], {self.ORDER_ID_2: "Order already matched"})

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_orders_falls_back_to_id_dict_when_get_order_fails(self, mock_delete, _mock_headers):
        mock_delete.return_value = {"canceled": [ORDER_ID], "not_canceled": {}}
        client = _make_client()
        client.get_order = MagicMock(side_effect=Exception("network error"))

        result = client.cancel_orders([ORDER_ID])

        self.assertEqual(result["canceled"], [{"id": ORDER_ID}])

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_orders_handles_empty_response(self, mock_delete, _mock_headers):
        mock_delete.return_value = {"canceled": [], "not_canceled": {}}
        client = _make_client()
        client.get_order = MagicMock()

        result = client.cancel_orders([])

        client.get_order.assert_not_called()
        self.assertEqual(result["canceled"], [])
        self.assertEqual(result["not_canceled"], {})

    @patch("py_clob_client.client.create_level_2_headers", return_value={})
    @patch("py_clob_client.client.delete")
    def test_cancel_orders_continues_after_single_get_order_failure(self, mock_delete, _mock_headers):
        ORDER_ID_3 = "0xghi789"
        FULL_ORDER_3 = {**FULL_ORDER, "id": ORDER_ID_3}
        mock_delete.return_value = {
            "canceled": [ORDER_ID, ORDER_ID_3],
            "not_canceled": {},
        }
        client = _make_client()
        client.get_order = MagicMock(
            side_effect=[Exception("transient error"), FULL_ORDER_3]
        )

        result = client.cancel_orders([ORDER_ID, ORDER_ID_3])

        self.assertEqual(len(result["canceled"]), 2)
        self.assertEqual(result["canceled"][0], {"id": ORDER_ID})
        self.assertEqual(result["canceled"][1], FULL_ORDER_3)
