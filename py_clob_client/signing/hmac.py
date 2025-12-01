import hmac
import hashlib
import base64
import json


def build_hmac_signature(
    secret: str, timestamp: str, method: str, requestPath: str, body=None
):
    """
    Creates an HMAC signature by signing a payload with the secret.

    Behavior:
    - If body is None or empty string, omit from message.
    - If body is a string, append verbatim (legacy behavior maintained).
    - If body is a dict/list, append canonical JSON (compact separators, sorted keys)
      to avoid encoding/ordering issues across languages.
    """
    base64_secret = base64.urlsafe_b64decode(secret)
    message = str(timestamp) + str(method) + str(requestPath)

    if body is not None and body != "":
        if isinstance(body, str):
            # Preserve legacy behavior: use provided JSON string as-is
            message += body
        else:
            # Canonicalize non-string bodies for cross-language parity
            message += json.dumps(body, separators=(",", ":"), sort_keys=True)

    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)

    # ensure base64 encoded
    return (base64.urlsafe_b64encode(h.digest())).decode("utf-8")
