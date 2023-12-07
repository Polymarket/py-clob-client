from unittest import TestCase

from py_clob_client.clob_types import (
    OrderArgs,
    OrderType,
    CreateOrderOptions,
)
from py_clob_client.constants import MUMBAI
from py_clob_client.order_builder.constants import BUY, SELL
from py_clob_client.signer import Signer
from py_clob_client.order_builder.builder import OrderBuilder
from py_clob_client.utilities import (
    parse_raw_orderbook_summary,
    generate_orderbook_summary_hash,
    order_to_json,
    is_tick_size_smaller,
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

    def test_order_to_json_0_1(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.1"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.1"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.1"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.1"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_01(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.01"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "5000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.01"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "5000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.01"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "5000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.01"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "5000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_001(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.001"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "500000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.001"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "500000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.001"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "500000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.001"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "500000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_0001(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.0001"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.0001"),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.0001"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.0001"),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_1_neg_risk(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.5,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_01_neg_risk(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "5000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "5000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "5000000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.05,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "5000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_001_neg_risk(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "500000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "500000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "500000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "500000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_order_to_json_0_0001_neg_risk(self):
        # publicly known private key
        private_key = (
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        )
        chain_id = MUMBAI
        signer = Signer(private_key=private_key, chain_id=chain_id)
        owner = "aaa-bbb-ccc"
        builder = OrderBuilder(signer)

        # GTC BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTC SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTC,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTC")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD BUY
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=BUY,
                ),
                options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "50000")
        self.assertEqual(json_order["order"]["takerAmount"], "100000000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "BUY")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

        # GTD SELL
        json_order = order_to_json(
            order=builder.create_order(
                order_args=OrderArgs(
                    token_id="100",
                    price=0.0005,
                    size=100,
                    side=SELL,
                ),
                options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
            ),
            owner=owner,
            orderType=OrderType.GTD,
        )

        self.assertIsNotNone(json_order)
        self.assertEqual(json_order["orderType"], "GTD")
        self.assertEqual(json_order["owner"], owner)
        self.assertIsNotNone(json_order["order"])
        self.assertIsNotNone(json_order["order"]["salt"])
        self.assertEqual(
            json_order["order"]["maker"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["signer"], "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        )
        self.assertEqual(
            json_order["order"]["taker"], "0x0000000000000000000000000000000000000000"
        )
        self.assertEqual(json_order["order"]["tokenId"], "100")
        self.assertEqual(json_order["order"]["makerAmount"], "100000000")
        self.assertEqual(json_order["order"]["takerAmount"], "50000")
        self.assertEqual(json_order["order"]["expiration"], "0")
        self.assertEqual(json_order["order"]["nonce"], "0")
        self.assertEqual(json_order["order"]["feeRateBps"], "0")
        self.assertEqual(json_order["order"]["side"], "SELL")
        self.assertEqual(json_order["order"]["signatureType"], 0)
        self.assertIsNotNone(json_order["order"]["signature"])

    def test_is_tick_size_smaller(self):
        # 0.1
        self.assertFalse(is_tick_size_smaller("0.1", "0.1"))
        self.assertFalse(is_tick_size_smaller("0.1", "0.01"))
        self.assertFalse(is_tick_size_smaller("0.1", "0.001"))
        self.assertFalse(is_tick_size_smaller("0.1", "0.0001"))

        # 0.01
        self.assertTrue(is_tick_size_smaller("0.01", "0.1"))
        self.assertFalse(is_tick_size_smaller("0.01", "0.01"))
        self.assertFalse(is_tick_size_smaller("0.01", "0.001"))
        self.assertFalse(is_tick_size_smaller("0.01", "0.0001"))

        # 0.001
        self.assertTrue(is_tick_size_smaller("0.001", "0.1"))
        self.assertTrue(is_tick_size_smaller("0.001", "0.01"))
        self.assertFalse(is_tick_size_smaller("0.001", "0.001"))
        self.assertFalse(is_tick_size_smaller("0.001", "0.0001"))

        # 0.0001
        self.assertTrue(is_tick_size_smaller("0.0001", "0.1"))
        self.assertTrue(is_tick_size_smaller("0.0001", "0.01"))
        self.assertTrue(is_tick_size_smaller("0.0001", "0.001"))
        self.assertFalse(is_tick_size_smaller("0.0001", "0.0001"))
