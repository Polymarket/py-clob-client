from unittest import TestCase

from py_clob_client.clob_types import OrderArgs
from py_clob_client.constants import MUMBAI
from py_clob_client.order_builder.constants import BUY, SELL

from py_clob_client.signer import Signer
from py_clob_client.order_builder.builder import OrderBuilder
from py_order_utils.model import POLY_GNOSIS_SAFE, EOA

# publicly known private key
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
chain_id = MUMBAI
signer = Signer(private_key=private_key, chain_id=chain_id)


class TestOrderBuilder(TestCase):
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
