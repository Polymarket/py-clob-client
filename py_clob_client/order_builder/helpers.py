from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_CEILING


def round_down(x: float, sig_digits: int) -> float:
    d = Decimal(str(x))
    return float(d.quantize(Decimal(10) ** -sig_digits, rounding=ROUND_FLOOR))


def round_normal(x: float, sig_digits: int) -> float:
    d = Decimal(str(x))
    return float(d.quantize(Decimal(10) ** -sig_digits, rounding=ROUND_HALF_EVEN))


def round_up(x: float, sig_digits: int) -> float:
    d = Decimal(str(x))
    return float(d.quantize(Decimal(10) ** -sig_digits, rounding=ROUND_CEILING))


def to_token_decimals(x: float) -> int:
    d = Decimal(str(x)) * Decimal("1000000")
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))


def decimal_places(x: float) -> int:
    return abs(Decimal(x.__str__()).as_tuple().exponent)
