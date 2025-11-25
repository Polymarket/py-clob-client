from poly_eip712_structs import EIP712Struct, Address, String, Uint

# Note: This file relies on the 'poly_eip712_structs' library for EIP-712 structure definitions.

class ClobAuth(EIP712Struct):
    """
    Defines the EIP-712 structure for Central Limit Order Book (CLOB) 
    authentication messages. This structure is typically signed by the user's 
    wallet to authenticate with the API for subsequent actions.
    
    Fields:
    - address: The Ethereum address of the user (or signer).
    - timestamp: The time of the message creation (often as a string for EIP-712).
    - nonce: A unique number to prevent replay attacks.
    - message: A custom descriptive message, often including a domain/app identifier.
    """
    address = Address()
    timestamp = String()
    nonce = Uint()
    message = String()
