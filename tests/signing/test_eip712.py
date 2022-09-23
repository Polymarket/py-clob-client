from unittest import TestCase
from py_clob_client.constants import MUMBAI

from py_clob_client.signer import Signer
from py_clob_client.signing.eip712 import sign_clob_auth_message

# publicly known private key
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
chain_id = MUMBAI
signer = Signer(private_key=private_key, chain_id=chain_id)


class TestEIP712(TestCase):
    def test_sign_clob_auth_message(self):
        signature = sign_clob_auth_message(signer, 10000000, 23)
        self.assertIsNotNone(signature)
        self.assertEqual(
            signature,
            "0xd91760ebcb14e814e9e12600b9bc7cd6bf13ebc175f6a28538b4925763f94f90012da34dd71290d441c28bc4f9b2281d3eb9ecfd1c9a63db1ce9ca85c89c914c1b",
        )
