import hmac
import hashlib
import base64


def build_hmac_signature(secret: str, timestamp: str, method: str, requestPath: str, body=None):
    """
    Signs an HMAC signature with the secret
    """
    base64_secret = base64.urlsafe_b64decode(secret)
    message = str(timestamp) + str(method) + str(requestPath)
    if body:
        message += str(body)

    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)

    # ensure base64 encoded
    return base64.urlsafe_b64encode(h.digest())


