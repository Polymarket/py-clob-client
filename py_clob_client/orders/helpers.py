from math import floor

def round_down(x: float, sig_digits: int)-> float:
    return floor(x * (10 ** sig_digits)) / (10 ** sig_digits)

def to_token_decimals(x: float)-> int:
    return int((10 ** 6) * x)
