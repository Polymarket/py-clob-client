from eip712_structs import EIP712Struct, Address, String

class ClobAuth(EIP712Struct):
    address = Address()
    timestamp = String()
    message = String()

