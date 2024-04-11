from unittest import TestCase
from py_clob_client.constants import AMOY

from py_clob_client.signer import Signer
from py_clob_client.signing.eip712 import sign_clob_auth_message

# publicly known private key
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
chain_id = AMOY
signer = Signer(private_key=private_key, chain_id=chain_id)


class TestEIP712(TestCase):
    def test_sign_clob_auth_message(self):
        signature = sign_clob_auth_message(signer, 10000000, 23)
        self.assertIsNotNone(signature)
        self.assertEqual(
            signature,
            "0xf62319a987514da40e57e2f4d7529f7bac38f0355bd88bb5adbb3768d80de6c1682518e0af677d5260366425f4361e7b70c25ae232aff0ab2331e2b164a1aedc1b",
        )
