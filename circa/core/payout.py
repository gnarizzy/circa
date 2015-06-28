from circa.settings import COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT
from decimal import *

def calc_payout(price):
    if price < COMMISSION_BREAKEVEN:
        payout = price - Decimal(COMMISSION_FLAT)
    elif price >= COMMISSION_BREAKEVEN and price * Decimal(COMMISSION_PERCENT) < 10:
        payout = Decimal(1-COMMISSION_PERCENT) * price
    else:
        payout = price - Decimal(10)  # Only take a max of $10

    return round(payout, 2)
