# General imports
from django.test import TestCase
from decimal import *
from django.test.utils import override_settings

# PayoutTest imports
from core.payout import calc_payout, COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_MAX

class PayoutTest(TestCase):

    def test_below_break_even(self):
        price = Decimal(COMMISSION_BREAKEVEN - 1)
        predicted_payout = round(price - Decimal(COMMISSION_FLAT), 2)
        payout = calc_payout(price)

        self.assertEqual(payout, predicted_payout)

    def test_above_break_even_below_max(self):
        price = Decimal(COMMISSION_BREAKEVEN + 1)
        predicted_payout = round(price - Decimal(price * Decimal(COMMISSION_PERCENT)), 2)
        payout = calc_payout(price)

        self.assertEqual(payout, predicted_payout)

    def test_above_max(self):
        price = Decimal((COMMISSION_MAX + 1) / COMMISSION_PERCENT)
        predicted_payout = round(price - Decimal(COMMISSION_MAX), 2)
        payout = calc_payout(price)

        self.assertEqual(payout, predicted_payout)

