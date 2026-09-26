from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")
MAX_MONEY = Decimal("9999999999.99")


def quantize_money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
