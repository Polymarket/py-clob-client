from unittest import TestCase
from unittest.mock import patch, MagicMock

from py_clob_client.http_helpers.helpers import set_proxy


class TestProxy(TestCase):
    @patch("py_clob_client.http_helpers.helpers.httpx.Client")
    def test_set_proxy_creates_client_with_proxy(self, mock_client_cls):
        """set_proxy should create a new httpx.Client with the proxy param."""
        set_proxy("http://localhost:8080")
        mock_client_cls.assert_called_once_with(http2=True, proxy="http://localhost:8080")

    @patch("py_clob_client.http_helpers.helpers.httpx.Client")
    def test_set_proxy_none_creates_client_without_proxy(self, mock_client_cls):
        """set_proxy(None) should create a client without the proxy param."""
        set_proxy(None)
        mock_client_cls.assert_called_once_with(http2=True)

    @patch("py_clob_client.http_helpers.helpers.httpx.Client")
    def test_set_proxy_empty_string_creates_client_without_proxy(self, mock_client_cls):
        """set_proxy('') should create a client without the proxy param."""
        set_proxy("")
        mock_client_cls.assert_called_once_with(http2=True)
