from decimal import *

COMMISSION_PERCENT = .15
COMMISSION_FLAT = 2.00
COMMISSION_BREAKEVEN = 13.33
COMMISSION_MAX = 10.00

def calc_payout(price):
    if price < COMMISSION_BREAKEVEN:
        payout = price - Decimal(COMMISSION_FLAT)
    elif price >= COMMISSION_BREAKEVEN and price * Decimal(COMMISSION_PERCENT) < COMMISSION_MAX:
        payout = Decimal(1-COMMISSION_PERCENT) * price
    else:
        payout = price - Decimal(COMMISSION_MAX)  # Only take a max of $10

    return round(payout, 2)
