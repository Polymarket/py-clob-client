from unittest import TestCase
import binascii

from py_clob_client.signing.hmac import build_hmac_signature


class TestHMAC(TestCase):
    def setUp(self):
        # Baseline inputs used across variation tests
        self.secret = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        self.timestamp = "1000000"
        self.method = "test-sign"
        self.path = "/orders"
        self.string_body = '{"hash": "0x123"}'  # legacy string body usage
        # Baseline signature from original test (string body form)
        self.baseline_signature = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, self.string_body
        )

    def test_build_hmac_signature_matches_expected(self):
        signature = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, self.string_body
        )
        self.assertIsNotNone(signature)
        self.assertEqual(
            "a3ZnZvcsH3ZwD7FuHGttDruLDurcl9PffnPSvac_bWQ=", signature
        )

    def test_dict_body_produces_different_signature_from_string_body(self):
        dict_body_sig = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, {"hash": "0x123"}
        )
        self.assertNotEqual(self.baseline_signature, dict_body_sig)

    def test_different_method_changes_signature(self):
        get_sig = build_hmac_signature(
            self.secret, self.timestamp, "GET", self.path, {"hash": "0x123"}
        )
        post_sig = build_hmac_signature(
            self.secret, self.timestamp, "POST", self.path, {"hash": "0x123"}
        )
        self.assertNotEqual(get_sig, post_sig)
        self.assertNotEqual(get_sig, self.baseline_signature)

    def test_different_timestamp_changes_signature(self):
        sig_new_time = build_hmac_signature(
            self.secret, "1000001", self.method, self.path, {"hash": "0x123"}
        )
        self.assertNotEqual(sig_new_time, self.baseline_signature)

    def test_different_path_changes_signature(self):
        sig_path = build_hmac_signature(
            self.secret, self.timestamp, self.method, "/api/v1/orders", {"hash": "0x123"}
        )
        self.assertNotEqual(sig_path, self.baseline_signature)

    def test_extra_key_and_ordering_affect_signature(self):
        sig_order1 = build_hmac_signature(
            self.secret,
            self.timestamp,
            self.method,
            self.path,
            {"hash": "0x123", "foo": "bar"},
        )
        sig_order2 = build_hmac_signature(
            self.secret,
            self.timestamp,
            self.method,
            self.path,
            {"foo": "bar", "hash": "0x123"},
        )
        self.assertNotEqual(sig_order1, self.baseline_signature)
        self.assertNotEqual(sig_order2, self.baseline_signature)
        self.assertNotEqual(sig_order1, sig_order2)

    def test_array_body_signature(self):
        sig_array = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, [1, 2, 3]
        )
        self.assertIsNotNone(sig_array)
        self.assertNotEqual(sig_array, self.baseline_signature)

    def test_unicode_body_signature(self):
        sig_unicode = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, {"emoji": "😃"}
        )
        self.assertIsNotNone(sig_unicode)
        self.assertNotEqual(sig_unicode, self.baseline_signature)

    def test_none_body_omitted_from_message(self):
        sig_none = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, None
        )
        self.assertNotEqual(sig_none, self.baseline_signature)

    def test_empty_string_body_omitted(self):
        sig_empty = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, ""
        )
        self.assertNotEqual(sig_empty, self.baseline_signature)

    def test_none_and_empty_body_same_signature(self):
        sig_none = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, None
        )
        sig_empty = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, ""
        )
        self.assertEqual(sig_none, sig_empty)

    def test_idempotent_same_inputs(self):
        sig1 = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, {"hash": "0x123"}
        )
        sig2 = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, {"hash": "0x123"}
        )
        self.assertEqual(sig1, sig2)

    def test_different_secret_changes_signature(self):
        other_secret = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        sig_other = build_hmac_signature(
            other_secret, self.timestamp, self.method, self.path, {"hash": "0x123"}
        )
        sig_original = build_hmac_signature(
            self.secret, self.timestamp, self.method, self.path, {"hash": "0x123"}
        )
        self.assertNotEqual(sig_other, sig_original)

    def test_invalid_secret_raises(self):
        with self.assertRaises(binascii.Error):
            build_hmac_signature(
                "!!!notbase64!!!",
                self.timestamp,
                self.method,
                self.path,
                {"hash": "0x123"},
            )
