from typing import Optional

import httpx


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: Optional[httpx.Response] = None, error_msg=None):
        assert resp is not None or error_msg is not None

        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        else:
            self.status_code = None
            self.error_msg = error_msg

    def _get_message(self, resp: httpx.Response):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return f"PolyApiException[status_code={self.status_code}, error_message={self.error_msg}]"

    def __str__(self):
        return self.__repr__()


class TickSizeRejectedError(PolyApiException):
    """
    Raised when an order is rejected and the error is likely due to tick size /
    price precision (e.g. the market's tick size changed on the CLOB). Clear the
    tick size cache and retry: client.clear_tick_size_cache() or
    client.clear_tick_size_cache(token_id), then create and post the order again.
    """

    def __init__(self, msg, api_exception=None):
        self.api_exception = api_exception
        hint = (
            "Clear tick size cache: client.clear_tick_size_cache() or "
            "client.clear_tick_size_cache(token_id), then create and post the order again."
        )
        self.msg = f"{msg}. {hint}"
        super().__init__(error_msg=self.msg)
        if api_exception is not None:
            self.status_code = api_exception.status_code

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"TickSizeRejectedError({self.msg!r})"
