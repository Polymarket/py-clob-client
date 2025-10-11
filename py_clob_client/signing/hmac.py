import hmac
import hashlib
import base64


def build_hmac_signature(
    secret: str, timestamp: str, method: str, requestPath: str, body=None
):
    """
    Creates an HMAC signature by signing a payload with the secret
    """
    # Add padding if necessary for proper base64 decoding
    secret_padded = secret + '=' * ((4 - len(secret) % 4) % 4)

    base64_secret = base64.urlsafe_b64decode(secret_padded)
    message = str(timestamp) + str(method) + str(requestPath)
    if body:
        # NOTE: Necessary to replace single quotes with double quotes
        # to generate the same hmac message as go and typescript
        message += str(body).replace("'", '"')

    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)

    # ensure base64 encoded
    return (base64.urlsafe_b64encode(h.digest())).decode("utf-8")
