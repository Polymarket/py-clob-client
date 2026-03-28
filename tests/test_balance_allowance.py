from unittest import TestCase

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import AMOY

# publicly known private key (Hardhat #0)
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
creds = ApiCreds(
    api_key="test-api-key",
    api_secret="test-api-secret",
    api_passphrase="test-api-passphrase",
)


class TestBalanceAllowance(TestCase):
    def test_get_balance_allowance_requires_params(self):
        client = ClobClient(
            "https://clob.polymarket.com",
            key=private_key,
            chain_id=AMOY,
            creds=creds,
        )
        with self.assertRaises(ValueError):
            client.get_balance_allowance()

    def test_update_balance_allowance_requires_params(self):
        client = ClobClient(
            "https://clob.polymarket.com",
            key=private_key,
            chain_id=AMOY,
            creds=creds,
        )
        with self.assertRaises(ValueError):
            client.update_balance_allowance()
