# General imports
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from decimal import *

# PayoutTest imports
from core.payout import calc_payout, COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_MAX

# ItemTest imports
from core.models import Item
from core.forms import ItemForm

# ListingTest imports
from core.models import Listing

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

class ItemTest(TestCase):

    def create_user(self):
        return User.objects.create_user(username='Juan', password='Pablo')

    def create_item(self, title="Object Name", description="Object Description"):
        return Item.objects.create(title=title, description=description)

    def test_item_creation(self):
        item = self.create_item()

        self.assertTrue(isinstance(item, Item))
        self.assertEqual("Object Name", item.__str__())

    def test_init_with_user(self):
        user = self.create_user()
        ItemForm(seller=user)

    def test_init_without_user(self):
        with self.assertRaises(KeyError):
            ItemForm()

    def test_valid_data(self):
        with open('static/other/test_image.jpg', 'rb') as fp:
            user = self.create_user()
            form = ItemForm({
                'title': "Penny",
                'description': "Just your average penny",
                'category': 1,
            }, {'photo': SimpleUploadedFile(fp.name, fp.read())}, seller=user)
            self.assertTrue(form.is_valid())
            item = form.save()
            self.assertEqual(item.title, "Penny")
            self.assertEqual(item.description, "Just your average penny")
            self.assertEqual(item.category, 1)
            self.assertIn('test_image', item.photo.name)

    def test_blank_data(self):
        user = self.create_user()
        form = ItemForm({}, seller=user)
        self.assertFalse(form.is_valid())
        print(form.errors)
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['This field is required.'],
            'photo': ['This field is required.'],
        })

class ListingTest(TestCase):

    def create_listing(self):
        return Listing.objects.create()

    def test_listing_creation(self):
        listing = self.create_listing()

        self.assertTrue(isinstance(listing, Listing))
        self.assertEqual(str(listing.id), listing.__str__())