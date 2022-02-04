from math import floor

COLLATERAL_TOKEN_DECIMALS = 6
CONDITIONAL_TOKEN_DECIMALS = 18

def round_down(x: float, sig_digits: int)-> float:
    return floor(x * (10 ** sig_digits)) / (10 ** sig_digits)

def to_collateral_token_decimals(x: float)-> int:
    return int((10 ** COLLATERAL_TOKEN_DECIMALS) * x)


def to_conditional_token_decimals(x: float)-> int:
    return int((10 ** CONDITIONAL_TOKEN_DECIMALS) * x)