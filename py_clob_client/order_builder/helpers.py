from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP, ROUND_CEILING


def round_down(x: float, sig_digits: int) -> float:
    exp = Decimal(1).scaleb(-sig_digits)
    return float(Decimal((str(x))).quantize(exp=exp, rounding=ROUND_FLOOR))


def round_normal(x: float, sig_digits: int) -> float:
    exp = Decimal(1).scaleb(-sig_digits)
    return float(Decimal((str(x))).quantize(exp=exp, rounding=ROUND_HALF_UP))


def round_up(x: float, sig_digits: int) -> float:
    exp = Decimal(1).scaleb(-sig_digits)
    return float(Decimal((str(x))).quantize(exp=exp, rounding=ROUND_CEILING))


def to_token_decimals(x: float) -> int:
    exp = Decimal(1)
    return int(
        (Decimal(str(x)) * Decimal(10**6)).quantize(exp=exp, rounding=ROUND_HALF_UP)
    )


def decimal_places(x: float) -> int:
    return abs(Decimal(x.__str__()).as_tuple().exponent)
