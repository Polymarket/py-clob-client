from unittest import TestCase

from py_clob_client.rfq.rfq_client import RfqClient
from py_clob_client.rfq.rfq_types import MatchType
from py_clob_client.order_builder.constants import BUY, SELL

class TestCreateAcceptQuotePayload(TestCase):
    
    def test_complementary(self):
        client = RfqClient(parent=None)
        quote = {
            "matchType": "COMPLEMENTARY",
            "side": BUY,
            "token": "tokenA",
            "sizeIn": "100", 
            "sizeOut": "50",
        }

        payload = client._get_request_order_creation_payload(quote)
        self.assertEqual(payload["token"], "tokenA")
        self.assertEqual(payload["side"], SELL)
        self.assertEqual(payload["size"], "100")

        quote = {
            "matchType": "COMPLEMENTARY",
            "side": SELL,
            "token": "tokenB",
            "sizeIn": "200",
            "sizeOut": "75",
        }

        payload = client._get_request_order_creation_payload(quote)
        self.assertEqual(payload["token"], "tokenB")
        self.assertEqual(payload["side"], BUY)
        self.assertEqual(payload["size"], "75")        


    def test_mint_merge(self):
        client = RfqClient(parent=None)
        quote = {
            "matchType": "MERGE",
            "side": BUY,
            "complement": "tokenC",
            "sizeIn": "30",
            "sizeOut": "15",
        }

        payload = client._get_request_order_creation_payload(quote)
        self.assertEqual(payload["token"], "tokenC")
        self.assertEqual(payload["side"], BUY)
        self.assertEqual(payload["size"], "30")

        quote = {
            "matchType": "MINT",
            "side": BUY,
            "complement": "tokenC",
            "sizeIn": "30",    # tokens bought
            "sizeOut": "15",
        }
        self.assertEqual(payload["token"], "tokenC")
        self.assertEqual(payload["side"], BUY)
        self.assertEqual(payload["size"], "30")
