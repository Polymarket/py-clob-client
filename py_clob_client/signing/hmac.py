import hmac
import hashlib
import base64
import json


def build_hmac_signature(
        secret: str, timestamp: str, method: str, requestPath: str, body=None
):
    """
    Builds an HMAC signature over: timestamp + METHOD(upper) + requestPath [+ body]

    Body handling:
    - None / empty string: omitted.
    - String: appended verbatim.
    - Other JSON types: serialized using compact JSON (no spaces) for deterministic, legacy parity.
    """
    base64_secret = base64.urlsafe_b64decode(secret)
    message = str(timestamp) + str(method).upper() + str(requestPath)

    if body is not None and body != "":
        if isinstance(body, str):
            message += body
        elif isinstance(body, (dict, list, int, float, bool)):
            message += json.dumps(body, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        else:
            raise TypeError("Unsupported body type for HMAC signing")

    h = hmac.new(base64_secret, message.encode("utf-8"), hashlib.sha256)
    return base64.urlsafe_b64encode(h.digest()).decode("utf-8")
