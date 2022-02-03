
from eth_account import Account


class Signer:
    def __init__(self, private_key):
        self.private_key = private_key
        self.account = Account.from_key(private_key)

    @property
    def address(self):
        return self.account.address

    def sign_hash(self, message_hash):
        """
        Signs a message hash
        """
        return Account._sign_hash(message_hash, self.private_key).signature.hex()