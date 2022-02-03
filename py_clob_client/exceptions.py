from requests import Response


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    
    def __init__(self, resp: Response=None, error_msg= None):
        assert(resp is not None or error_msg is not None)
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None
    
    def _get_message(self, resp: Response):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(self.status_code, self.error_msg)

    def __str__(self):
        return self.__repr__()