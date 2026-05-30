"""Tests for ClobClient error message handling (tick size detection)."""
from unittest import TestCase

from py_clob_client.client import ClobClient


class TestClientTickSizeErrorDetection(TestCase):
    """Test _is_tick_size_related_error and _flatten_error_message with dict/string payloads."""

    def test_is_tick_size_related_error_string_plain(self):
        self.assertTrue(ClobClient._is_tick_size_related_error("invalid tick size"))
        self.assertTrue(ClobClient._is_tick_size_related_error("Price precision error"))
        self.assertTrue(ClobClient._is_tick_size_related_error("minimum_tick violated"))
        self.assertFalse(ClobClient._is_tick_size_related_error("insufficient balance"))
        self.assertFalse(ClobClient._is_tick_size_related_error(""))

    def test_is_tick_size_related_error_string_none(self):
        self.assertFalse(ClobClient._is_tick_size_related_error(None))

    def test_is_tick_size_related_error_dict_nested_message(self):
        # API returns resp.json() e.g. {"error": {"message": "invalid tick size"}}
        payload = {"error": {"message": "invalid tick size"}}
        self.assertTrue(ClobClient._is_tick_size_related_error(payload))

    def test_is_tick_size_related_error_dict_precision_deep(self):
        payload = {"detail": {"reason": "Price precision does not match"}}
        self.assertTrue(ClobClient._is_tick_size_related_error(payload))

    def test_is_tick_size_related_error_dict_minimum_tick(self):
        payload = {"message": "Order violates minimum_tick"}
        self.assertTrue(ClobClient._is_tick_size_related_error(payload))

    def test_is_tick_size_related_error_dict_unrelated(self):
        payload = {"error": {"message": "insufficient balance"}}
        self.assertFalse(ClobClient._is_tick_size_related_error(payload))

    def test_flatten_error_message_string(self):
        self.assertEqual(ClobClient._flatten_error_message("hello"), "hello")

    def test_flatten_error_message_dict_nested(self):
        payload = {"error": {"message": "invalid tick size"}}
        self.assertEqual(
            ClobClient._flatten_error_message(payload), "invalid tick size"
        )

    def test_flatten_error_message_dict_multiple_keys(self):
        payload = {"msg": "precision", "code": 400}
        self.assertIn("precision", ClobClient._flatten_error_message(payload))

    def test_flatten_error_message_list(self):
        payload = ["first", "minimum_tick error"]
        self.assertIn("minimum_tick", ClobClient._flatten_error_message(payload))

    def test_flatten_error_message_none(self):
        self.assertEqual(ClobClient._flatten_error_message(None), "")
