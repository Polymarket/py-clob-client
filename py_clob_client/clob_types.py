from dataclasses import dataclass

@dataclass
class ApiCreds:
    api_key: str
    api_secret: str
    api_passphrase: str