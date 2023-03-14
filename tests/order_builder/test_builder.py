from unittest import TestCase

from py_clob_client.clob_types import OrderArgs
from py_clob_client.constants import MUMBAI
from py_clob_client.order_builder.constants import BUY, SELL

from py_clob_client.signer import Signer
from py_clob_client.order_builder.builder import OrderBuilder
from py_clob_client.order_builder.helpers import decimal_places
from py_order_utils.model import POLY_GNOSIS_SAFE, EOA

# publicly known private key
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
chain_id = MUMBAI
signer = Signer(private_key=private_key, chain_id=chain_id)


class TestOrderBuilder(TestCase):
    def test_get_order_amounts_buy(self):
        builder = OrderBuilder(signer)

        delta = 0.01
        size = 0.01
        while size <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(BUY, size, price)
                self.assertEqual(side, 0)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                price = price + delta

            size = size + delta

    def test_get_order_amounts_sell(self):
        builder = OrderBuilder(signer)

        delta = 0.01
        size = 0.01
        while size <= 100:
            price = 0.01
            while price <= 1:
                side, maker, taker = builder.get_order_amounts(SELL, size, price)
                self.assertEqual(side, 1)
                self.assertEqual(decimal_places(maker), 0)
                self.assertEqual(decimal_places(taker), 0)
                price = price + delta

            size = size + delta

    def test_create_order_decimal_accuracy(self):
        builder = OrderBuilder(signer)

        # BUY
        signed_order = builder.create_order(
            order_args=OrderArgs(
                token_id="123",
                price=0.24,
                size=15,
                side=BUY,
            )
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
            )
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
            )
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
            )
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
            )
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
            )
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
            )
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
            )
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
            )
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

    def test_create_order_buy(self):
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
            )
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
            int(signed_order.order["makerAmount"])
            / int(signed_order.order["takerAmount"]),
            0.56,
        )

    def test_create_order_sell(self):
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
            )
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
            int(signed_order.order["takerAmount"])
            / int(signed_order.order["makerAmount"]),
            0.56,
        )

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
            )
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
            )
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
