from unittest import TestCase

from py_clob_client.utilities import (
    parse_raw_orderbook_summary,
    generate_orderbook_summary_hash,
)


class TestUtilities(TestCase):
    def test_parse_raw_orderbook_summary(self):
        raw_obs = {
            "market": "0xbd31dc8a20211944f6b70f31557f1001557b59905b7738480ca09bd4532f84af",
            "asset_id": "1343197538147866997676250008839231694243646439454152539053893078719042421992",
            "bids": [
                {"price": "0.15", "size": "100"},
                {"price": "0.31", "size": "148.56"},
                {"price": "0.33", "size": "58"},
                {"price": "0.5", "size": "100"},
            ],
            "asks": [],
            "hash": "9d6d9e8831a150ac4cd878f99f7b2c6d419b875f",
        }

        orderbook_summary = parse_raw_orderbook_summary(raw_obs)

        self.assertEqual(
            orderbook_summary.market,
            "0xbd31dc8a20211944f6b70f31557f1001557b59905b7738480ca09bd4532f84af",
        )
        self.assertEqual(
            orderbook_summary.asset_id,
            "1343197538147866997676250008839231694243646439454152539053893078719042421992",
        )
        self.assertEqual(
            orderbook_summary.hash, "9d6d9e8831a150ac4cd878f99f7b2c6d419b875f"
        )

        self.assertIsNotNone(orderbook_summary.asks)
        self.assertIsNotNone(orderbook_summary.bids)

        self.assertEqual(len(orderbook_summary.asks), 0)
        self.assertEqual(len(orderbook_summary.bids), 4)

        self.assertEqual(orderbook_summary.bids[0].price, "0.15")
        self.assertEqual(orderbook_summary.bids[0].size, "100")
        self.assertEqual(orderbook_summary.bids[1].price, "0.31")
        self.assertEqual(orderbook_summary.bids[1].size, "148.56")
        self.assertEqual(orderbook_summary.bids[2].price, "0.33")
        self.assertEqual(orderbook_summary.bids[2].size, "58")
        self.assertEqual(orderbook_summary.bids[3].price, "0.5")
        self.assertEqual(orderbook_summary.bids[3].size, "100")

        raw_obs = {
            "market": "0xaabbcc",
            "asset_id": "100",
            "bids": [],
            "asks": [],
            "hash": "7f81a35a09e1933a96b05edb51ac4be4a6163146",
        }

        orderbook_summary = parse_raw_orderbook_summary(raw_obs)

        self.assertEqual(
            orderbook_summary.market,
            "0xaabbcc",
        )
        self.assertEqual(
            orderbook_summary.asset_id,
            "100",
        )
        self.assertEqual(
            orderbook_summary.hash, "7f81a35a09e1933a96b05edb51ac4be4a6163146"
        )

        self.assertIsNotNone(orderbook_summary.asks)
        self.assertIsNotNone(orderbook_summary.bids)

        self.assertEqual(len(orderbook_summary.asks), 0)
        self.assertEqual(len(orderbook_summary.bids), 0)

    def test_generate_orderbook_summary_hash(self):
        raw_obs = {
            "market": "0xaabbcc",
            "asset_id": "100",
            "bids": [
                {"price": "0.3", "size": "100"},
                {"price": "0.4", "size": "100"},
            ],
            "asks": [
                {"price": "0.6", "size": "100"},
                {"price": "0.7", "size": "100"},
            ],
            "hash": "",
        }

        orderbook_summary = parse_raw_orderbook_summary(raw_obs)
        self.assertEqual(
            generate_orderbook_summary_hash(orderbook_summary),
            "b8b72c72c6534d1b3a4e7fb47b81672d0e94d5a5",
        )
        self.assertEqual(
            orderbook_summary.hash,
            "b8b72c72c6534d1b3a4e7fb47b81672d0e94d5a5",
        )

        raw_obs = {
            "market": "0xaabbcc",
            "asset_id": "100",
            "bids": [
                {"price": "0.3", "size": "100"},
                {"price": "0.4", "size": "100"},
            ],
            "asks": [
                {"price": "0.6", "size": "100"},
                {"price": "0.7", "size": "100"},
            ],
            "hash": "b8b72c72c6534d1b3a4e7fb47b81672d0e94d5a5",
        }

        orderbook_summary = parse_raw_orderbook_summary(raw_obs)
        self.assertEqual(
            generate_orderbook_summary_hash(orderbook_summary),
            "b8b72c72c6534d1b3a4e7fb47b81672d0e94d5a5",
        )
        self.assertEqual(
            orderbook_summary.hash,
            "b8b72c72c6534d1b3a4e7fb47b81672d0e94d5a5",
        )

        raw_obs = {
            "market": "0xaabbcc",
            "asset_id": "100",
            "bids": [],
            "asks": [],
            "hash": "",
        }

        orderbook_summary = parse_raw_orderbook_summary(raw_obs)
        self.assertEqual(
            generate_orderbook_summary_hash(orderbook_summary),
            "7f81a35a09e1933a96b05edb51ac4be4a6163146",
        )
        self.assertEqual(
            orderbook_summary.hash,
            "7f81a35a09e1933a96b05edb51ac4be4a6163146",
        )
