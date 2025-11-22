from unittest import TestCase

from py_clob_client.signing.hmac import build_hmac_signature


class TestHMAC(TestCase):
    def test_build_hmac_signature(self):
        signature = build_hmac_signature(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            "1000000",
            "test-sign",
            "/orders",
            '{"hash": "0x123"}',
        )
        self.assertIsNotNone(signature)
        self.assertEqual(
            "a3ZnZvcsH3ZwD7FuHGttDruLDurcl9PffnPSvac_bWQ=",
            signature,
        )
