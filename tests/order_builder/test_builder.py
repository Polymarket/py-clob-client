from unittest import TestCase

from py_clob_client.clob_types import (
    OrderArgs,
    MarketOrderArgs,
    CreateOrderOptions,
    OrderSummary,
    OrderType,
)
from py_clob_client.constants import AMOY
from py_clob_client.order_builder.constants import BUY, SELL

from py_clob_client.signer import Signer
from py_clob_client.order_builder.builder import OrderBuilder, ROUNDING_CONFIG
from py_clob_client.order_builder.helpers import decimal_places, round_normal
from py_order_utils.model import (
    POLY_GNOSIS_SAFE,
    EOA,
    BUY as UtilsBuy,
    SELL as UtilsSell,
)

# publicly known private key
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
chain_id = AMOY
signer = Signer(private_key=private_key, chain_id=chain_id)


class TestOrderBuilder(TestCase):
    def test_calculate_buy_market_price_FOK(self):
        # empty
        with self.assertRaises(Exception):
            builder = OrderBuilder(signer)
            builder.calculate_buy_market_price([], 100, OrderType.FOK)

        # not enough
        with self.assertRaises(Exception):
            positions = [
                OrderSummary(price="0.5", size="100"),
                OrderSummary(price="0.4", size="100"),
            ]
            builder = OrderBuilder(signer)
            builder.calculate_buy_market_price(positions, 100, OrderType.FOK)

        # OK
        positions = [
            OrderSummary(price="0.5", size="100"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FOK), 0.5
        )

        positions = [
            OrderSummary(price="0.5", size="100"),
            OrderSummary(price="0.4", size="200"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FOK), 0.4
        )

        positions = [
            OrderSummary(price="0.5", size="120"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FOK), 0.5
        )

        positions = [
            OrderSummary(price="0.5", size="200"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FOK), 0.5
        )

    def test_calculate_sell_market_price_FOK(self):
        # empty
        with self.assertRaises(Exception):
            builder = OrderBuilder(signer)
            builder.calculate_sell_market_price([], 100)

        # not enough
        with self.assertRaises(Exception):
            positions = [
                OrderSummary(price="0.4", size="10"),
                OrderSummary(price="0.5", size="10"),
            ]
            builder = OrderBuilder(signer)
            builder.calculate_sell_market_price(positions, 100, OrderType.FOK)

        # OK
        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FOK), 0.5
        )

        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="300"),
            OrderSummary(price="0.5", size="10"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FOK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="200"),
            OrderSummary(price="0.5", size="10"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FOK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="300"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 200, OrderType.FOK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="334"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 300, OrderType.FOK), 0.3
        )

    def test_calculate_buy_market_price_FAK(self):
        # empty
        with self.assertRaises(Exception):
            builder = OrderBuilder(signer)
            builder.calculate_buy_market_price([], 100, OrderType.FAK)

        # not enough
        positions = [
            OrderSummary(price="0.5", size="100"),
            OrderSummary(price="0.4", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FAK), 0.5
        )

        # OK
        positions = [
            OrderSummary(price="0.5", size="100"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FAK), 0.5
        )

        positions = [
            OrderSummary(price="0.5", size="100"),
            OrderSummary(price="0.4", size="200"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FAK), 0.4
        )

        positions = [
            OrderSummary(price="0.5", size="120"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FAK), 0.5
        )

        positions = [
            OrderSummary(price="0.5", size="200"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.3", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_buy_market_price(positions, 100, OrderType.FAK), 0.5
        )

    def test_calculate_sell_market_price_FAK(self):
        # empty
        with self.assertRaises(Exception):
            builder = OrderBuilder(signer)
            builder.calculate_sell_market_price([], 100)

        # not enough
        positions = [
            OrderSummary(price="0.4", size="10"),
            OrderSummary(price="0.5", size="10"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FAK), 0.4
        )

        # OK
        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FAK), 0.5
        )

        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="300"),
            OrderSummary(price="0.5", size="10"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FAK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="100"),
            OrderSummary(price="0.4", size="200"),
            OrderSummary(price="0.5", size="10"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 100, OrderType.FAK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="300"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 200, OrderType.FAK), 0.4
        )

        positions = [
            OrderSummary(price="0.3", size="334"),
            OrderSummary(price="0.4", size="100"),
            OrderSummary(price="0.5", size="100"),
        ]
        builder = OrderBuilder(signer)
        self.assertEqual(
            builder.calculate_sell_market_price(positions, 300, OrderType.FAK), 0.3
        )

    def test_get_market_order_amounts_buy_0_1(self):
        builder = OrderBuilder(signer)

        delta_price = 0.1
        delta_size = 0.01
        amount = 0.01
        while amount <= 1000:
            price = 0.1
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    BUY, amount, price, ROUNDING_CONFIG["0.1"]
                )
                self.assertEqual(side, UtilsBuy)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 2), round_normal(price, 2)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_buy_0_01(self):
        builder = OrderBuilder(signer)

        delta_price = 0.01
        delta_size = 0.01
        amount = 0.01
        while amount <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    BUY, amount, price, ROUNDING_CONFIG["0.01"]
                )
                self.assertEqual(side, UtilsBuy)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 4), round_normal(price, 4)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_buy_0_001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.001
        delta_size = 0.01
        amount = 0.01
        while amount <= 10:
            price = 0.001
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    BUY, amount, price, ROUNDING_CONFIG["0.001"]
                )
                self.assertEqual(side, UtilsBuy)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 6), round_normal(price, 6)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_buy_0_0001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.0001
        delta_size = 0.01
        amount = 0.01
        while amount <= 1:
            price = 0.0001
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    BUY, amount, price, ROUNDING_CONFIG["0.0001"]
                )
                self.assertEqual(side, UtilsBuy)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 8), round_normal(price, 8)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_sell_0_1(self):
        builder = OrderBuilder(signer)

        delta_price = 0.1
        delta_size = 0.01
        amount = 0.01
        while amount <= 1000:
            price = 0.1
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    SELL, amount, price, ROUNDING_CONFIG["0.1"]
                )
                self.assertEqual(side, UtilsSell)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 2), round_normal(price, 2)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_sell_0_01(self):
        builder = OrderBuilder(signer)

        delta_price = 0.01
        delta_size = 0.01
        amount = 0.01
        while amount <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    SELL, amount, price, ROUNDING_CONFIG["0.01"]
                )
                self.assertEqual(side, UtilsSell)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 4), round_normal(price, 4)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_sell_0_001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.001
        delta_size = 0.01
        amount = 0.01
        while amount <= 10:
            price = 0.001
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    SELL, amount, price, ROUNDING_CONFIG["0.001"]
                )
                self.assertEqual(side, UtilsSell)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 6), round_normal(price, 6)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_market_order_amounts_sell_0_0001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.0001
        delta_size = 0.01
        amount = 0.01
        while amount <= 1:
            price = 0.0001
            while price <= 1:
                side, maker, taker = builder.get_market_order_amounts(
                    SELL, amount, price, ROUNDING_CONFIG["0.0001"]
                )
                self.assertEqual(side, UtilsSell)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(taker / maker, 8), round_normal(price, 8)
                )
                price = price + delta_price

            amount = amount + delta_size

    def test_get_order_amounts_buy_0_1(self):
        builder = OrderBuilder(signer)

        delta_price = 0.1
        delta_size = 0.01
        size = 0.01
        while size <= 1000:
            price = 0.1
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    BUY, size, price, ROUNDING_CONFIG["0.1"]
                )
                self.assertEqual(side, 0)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 2), round_normal(price, 2)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_buy_0_01(self):
        builder = OrderBuilder(signer)

        delta_price = 0.01
        delta_size = 0.01
        size = 0.01
        while size <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    BUY, size, price, ROUNDING_CONFIG["0.01"]
                )
                self.assertEqual(side, 0)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 4), round_normal(price, 4)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_buy_0_001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.001
        delta_size = 0.01
        size = 0.01
        while size <= 10:
            price = 0.001
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    BUY, size, price, ROUNDING_CONFIG["0.001"]
                )
                self.assertEqual(side, 0)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 6), round_normal(price, 6)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_buy_0_0001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.0001
        delta_size = 0.01
        size = 0.01
        while size <= 1:
            price = 0.0001
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    BUY, size, price, ROUNDING_CONFIG["0.0001"]
                )
                self.assertEqual(side, 0)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(maker / taker, 8), round_normal(price, 8)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_sell_0_1(self):
        builder = OrderBuilder(signer)

        delta_price = 0.1
        delta_size = 0.01
        size = 0.01
        while size <= 1000:
            price = 0.1
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    SELL, size, price, ROUNDING_CONFIG["0.1"]
                )
                self.assertEqual(side, 1)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(taker / maker, 2), round_normal(price, 2)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_sell_0_01(self):
        builder = OrderBuilder(signer)

        delta_price = 0.01
        delta_size = 0.01
        size = 0.01
        while size <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    SELL, size, price, ROUNDING_CONFIG["0.01"]
                )
                self.assertEqual(side, 1)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(taker / maker, 4), round_normal(price, 4)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_sell_0_001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.001
        delta_size = 0.01
        size = 0.01
        while size <= 10:
            price = 0.001
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    SELL, size, price, ROUNDING_CONFIG["0.001"]
                )
                self.assertEqual(side, 1)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(taker / maker, 6), round_normal(price, 6)
                )
                price = price + delta_price

            size = size + delta_size

    def test_get_order_amounts_sell_0_0001(self):
        builder = OrderBuilder(signer)

        delta_price = 0.0001
        delta_size = 0.01
        size = 0.01
        while size <= 1:
            price = 0.0001
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(
                    SELL, size, price, ROUNDING_CONFIG["0.0001"]
                )
                self.assertEqual(side, 1)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                self.assertGreaterEqual(
                    round_normal(taker / maker, 8), round_normal(price, 8)
                )
                price = price + delta_price

            size = size + delta_size

    def test_create_order_decimal_accuracy(self):
        builder = OrderBuilder(signer)

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.24,
                size=15,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            3600000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            15000000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.24,
                size=15,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            15000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            3600000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.82,
                size=101,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            82820000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            101000000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.82,
                size=101,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            101000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            82820000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.78,
                size=12.8205,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            9999600,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            12820000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.78,
                size=12.8205,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            12820000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            9999600,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.39,
                size=2435.89,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            2435890000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            949997100,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.43,
                size=19.1,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            19100000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            8213000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.58,
                size=18233.33,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            10575331400,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            18233330000,
        )
        self.assertEqual(
            signed_order.order["makerAmount"] / signed_order.order["takerAmount"], 0.58
        )

    def test_create_order_buy_0_1(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.5,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            10520000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.5,
        )

    def test_create_order_buy_0_01(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            11782400,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.56,
        )

    def test_create_order_buy_0_001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.056,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            1178240,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.056,
        )

    def test_create_order_buy_0_0001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.0056,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            117824,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.0056,
        )

    def test_create_order_sell_0_1(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.5,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            10520000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.5,
        )

    def test_create_order_sell_0_01(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            11782400,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.56,
        )

    def test_create_order_sell_0_001(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.056,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            1178240,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.056,
        )

    def test_create_order_sell_0_0001(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.0056,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            117824,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.0056,
        )

    def test_create_order_decimal_accuracy_neg_risk(self):
        builder = OrderBuilder(signer)

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.24,
                size=15,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            3600000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            15000000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.24,
                size=15,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            15000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            3600000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.82,
                size=101,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            82820000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            101000000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.82,
                size=101,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            101000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            82820000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.78,
                size=12.8205,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            9999600,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            12820000,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.78,
                size=12.8205,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            12820000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            9999600,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.39,
                size=2435.89,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            2435890000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            949997100,
        )

        # SELL
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.43,
                size=19.1,
                side=SELL,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            19100000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            8213000,
        )

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.58,
                size=18233.33,
                side=BUY,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            10575331400,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            18233330000,
        )
        self.assertEqual(
            signed_order.order["makerAmount"] / signed_order.order["takerAmount"], 0.58
        )

    def test_create_order_buy_0_1_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.5,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            10520000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.5,
        )

    def test_create_order_buy_0_01_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            11782400,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.56,
        )

    def test_create_order_buy_0_001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.056,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            1178240,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.056,
        )

    def test_create_order_buy_0_0001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.0056,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            117824,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.0056,
        )

    def test_create_order_sell_0_1_neg_risk(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.5,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            10520000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.5,
        )

    def test_create_order_sell_0_01_neg_risk(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            11782400,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.56,
        )

    def test_create_order_sell_0_001_neg_risk(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.056,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            1178240,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.056,
        )

    def test_create_order_sell_0_0001_neg_risk(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.0056,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            21040000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            117824,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            50000,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.0056,
        )

    def test_dict_order_buy_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertIsNotNone(signed_order)

        signed_order_dict = signed_order.dict()

        self.assertIsNotNone(signed_order_dict)
        self.assertTrue(isinstance(signed_order_dict["salt"], int))
        self.assertEqual(
            signed_order_dict["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order_dict["tokenId"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["makerAmount"],
            "11782400",
        )
        self.assertEqual(
            signed_order_dict["takerAmount"],
            "21040000",
        )
        self.assertEqual(
            signed_order_dict["side"],
            BUY,
        )
        self.assertEqual(
            signed_order_dict["expiration"],
            "50000",
        )
        self.assertEqual(
            signed_order_dict["nonce"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["feeRateBps"],
            "111",
        )
        self.assertEqual(
            signed_order_dict["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order_dict["signature"])

    def test_dict_order_sell_neg_risk(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertIsNotNone(signed_order)

        signed_order_dict = signed_order.dict()

        self.assertIsNotNone(signed_order_dict)
        self.assertTrue(isinstance(signed_order_dict["salt"], int))
        self.assertEqual(
            signed_order_dict["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order_dict["tokenId"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["makerAmount"],
            "21040000",
        )
        self.assertEqual(
            signed_order_dict["takerAmount"],
            "11782400",
        )
        self.assertEqual(
            signed_order_dict["side"],
            SELL,
        )
        self.assertEqual(
            signed_order_dict["expiration"],
            "50000",
        )
        self.assertEqual(
            signed_order_dict["nonce"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["feeRateBps"],
            "111",
        )
        self.assertEqual(
            signed_order_dict["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order_dict["signature"])

    def test_dict_order_buy(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=BUY,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertIsNotNone(signed_order)

        signed_order_dict = signed_order.dict()

        self.assertIsNotNone(signed_order_dict)
        self.assertTrue(isinstance(signed_order_dict["salt"], int))
        self.assertEqual(
            signed_order_dict["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order_dict["tokenId"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["makerAmount"],
            "11782400",
        )
        self.assertEqual(
            signed_order_dict["takerAmount"],
            "21040000",
        )
        self.assertEqual(
            signed_order_dict["side"],
            BUY,
        )
        self.assertEqual(
            signed_order_dict["expiration"],
            "50000",
        )
        self.assertEqual(
            signed_order_dict["nonce"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["feeRateBps"],
            "111",
        )
        self.assertEqual(
            signed_order_dict["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order_dict["signature"])

    def test_dict_order_sell(self):
        builder = OrderBuilder(signer, sig_type=POLY_GNOSIS_SAFE)

        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.56,
                size=21.04,
                side=SELL,
                fee_rate_bps=111,
                nonce=123,
                expiration=50000,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertIsNotNone(signed_order)

        signed_order_dict = signed_order.dict()

        self.assertIsNotNone(signed_order_dict)
        self.assertTrue(isinstance(signed_order_dict["salt"], int))
        self.assertEqual(
            signed_order_dict["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order_dict["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order_dict["tokenId"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["makerAmount"],
            "21040000",
        )
        self.assertEqual(
            signed_order_dict["takerAmount"],
            "11782400",
        )
        self.assertEqual(
            signed_order_dict["side"],
            SELL,
        )
        self.assertEqual(
            signed_order_dict["expiration"],
            "50000",
        )
        self.assertEqual(
            signed_order_dict["nonce"],
            "123",
        )
        self.assertEqual(
            signed_order_dict["feeRateBps"],
            "111",
        )
        self.assertEqual(
            signed_order_dict["signatureType"],
            POLY_GNOSIS_SAFE,
        )
        self.assertIsNotNone(signed_order_dict["signature"])

    def test_create_market_order_buy_0_1(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.5,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            200000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.5,
        )

    def test_create_market_order_buy_0_01(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.56,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            178571400,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.56,
        )

    def test_create_market_order_buy_0_001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            1785714280,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.056,
        )

    def test_create_market_order_buy_0_0001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.0056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            17857142857,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.0056,
        )

    def test_create_market_order_buy_0_1_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.5,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            200000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.5,
        )

    def test_create_market_order_buy_0_01_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.56,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            178571400,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.56,
        )

    def test_create_market_order_buy_0_001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            1785714280,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.056,
        )

    def test_create_market_order_buy_0_0001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=BUY,
                token_id="123",
                price=0.0056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            17857142857,
        )
        self.assertEqual(
            signed_order.order["side"],
            0,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["makerAmount"])
            / float(signed_order.order["takerAmount"]),
            0.0056,
        )

    def test_create_market_order_sell_0_1(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.5,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            50000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.5,
        )

    def test_create_market_order_sell_0_01(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.56,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            56000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.56,
        )

    def test_create_market_order_sell_0_001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            5600000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.056,
        )

    def test_create_market_order_sell_0_0001(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.0056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=False),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            560000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.0056,
        )

    def test_create_market_order_sell_0_1_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.5,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.1", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            50000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.5,
        )

    def test_create_market_order_sell_0_01_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.56,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.01", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            56000000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.56,
        )

    def test_create_market_order_sell_0_001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            5600000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.056,
        )

    def test_create_market_order_sell_0_0001_neg_risk(self):
        builder = OrderBuilder(signer)

        signed_order = builder.create_market_order(
            order_args=MarketOrderArgs(
                side=SELL,
                token_id="123",
                price=0.0056,
                amount=100,
                fee_rate_bps=111,
                nonce=123,
            ),
            options=CreateOrderOptions(tick_size="0.0001", neg_risk=True),
        )

        self.assertTrue(isinstance(signed_order.order["salt"], int))
        self.assertIsNotNone(signed_order)
        self.assertEqual(
            signed_order.order["maker"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["signer"],
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        )
        self.assertEqual(
            signed_order.order["taker"],
            "0x0000000000000000000000000000000000000000",
        )
        self.assertEqual(
            signed_order.order["tokenId"],
            123,
        )
        self.assertEqual(
            signed_order.order["makerAmount"],
            100000000,
        )
        self.assertEqual(
            signed_order.order["takerAmount"],
            560000,
        )
        self.assertEqual(
            signed_order.order["side"],
            1,
        )
        self.assertEqual(
            signed_order.order["expiration"],
            0,
        )
        self.assertEqual(
            signed_order.order["nonce"],
            123,
        )
        self.assertEqual(
            signed_order.order["feeRateBps"],
            111,
        )
        self.assertEqual(
            signed_order.order["signatureType"],
            EOA,
        )
        self.assertIsNotNone(signed_order.signature)
        self.assertGreaterEqual(
            float(signed_order.order["takerAmount"])
            / float(signed_order.order["makerAmount"]),
            0.0056,
        )
