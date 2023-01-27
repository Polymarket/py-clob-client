from unittest import TestCase

from py_clob_client.order_builder.helpers import decimal_places


class TestHelpers(TestCase):
    def test_decimal_places(self):
        self.assertEqual(decimal_places(949.9970999999999), 13)
        self.assertEqual(decimal_places(949), 0)
