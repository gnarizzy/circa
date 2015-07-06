# General imports
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from decimal import *

# PayoutTest imports
from core.payout import calc_payout, COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_MAX

# ItemTest imports
from core.models import Item
from core.forms import ItemForm

# ListingTest imports
from core.models import Listing
from core.forms import ListingForm

# EditListingTest imports
from core.forms import EditListingForm

# OfferTest imports
from core.forms import OfferForm

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
                'category': '1',
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
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['This field is required.'],
            'photo': ['This field is required.'],
        })

    def test_invalid_category(self):
        with open('static/other/test_image.jpg', 'rb') as fp:
            user = self.create_user()
            form = ItemForm({
                'title': "Penny",
                'description': "Just your average penny",
                'category': '0',
            }, {'photo': SimpleUploadedFile(fp.name, fp.read())}, seller=user)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors, {
                'category': ['You must choose a category for your item.'],
            })

class ListingTest(TestCase):

    def create_listing(self):
        return Listing.objects.create()

    def create_item(self, title="Object Name", description="Object Description"):
        return Item.objects.create(title=title, description=description)

    def test_listing_creation(self):
        listing = self.create_listing()

        self.assertTrue(isinstance(listing, Listing))
        self.assertEqual(str(listing.id), listing.__str__())

    def test_init_with_item(self):
        item = self.create_item()
        ListingForm(item=item)

    def test_init_without_item(self):
        with self.assertRaises(KeyError):
            ListingForm()

    def test_valid_data(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 100,
            'buy_now_price': 200,
            'zipcode': 30313,
        }, item=item)
        self.assertTrue(form.is_valid())
        listing = form.save()
        self.assertEqual(listing.starting_offer, 100)
        self.assertEqual(listing.buy_now_price, 200)
        self.assertEqual(listing.zipcode, 30313)
        self.assertEqual(listing.id, item.listing.id)

    def test_blank_data(self):
        item = self.create_item()
        form = ListingForm({}, item=item)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'starting_offer': ['This field is required.'],
            'buy_now_price': ['This field is required.'],
            'zipcode': ['This field is required.'],
        })

    def test_invalid_starting_offer(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 4,
            'buy_now_price': 20,
            'zipcode': 30313,
        }, item=item)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'starting_offer': ['The minimum starting offer is $5.00.'],
            'buy_now_price': ['Buy now price must be at least 10% higher than starting offer, which must '
                              'be at least $5.00.'],
        })

    def test_invalid_buy_now_price(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 100,
            'buy_now_price': 101,
            'zipcode': 30313,
        }, item=item)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'buy_now_price': ['Buy now price must be at least 10% higher than starting offer.'],
        })

    def test_invalid_zip_code(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 5,
            'buy_now_price': 100,
            'zipcode': 90210,
        }, item=item)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'zipcode': ['Unfortunately, Circa is not yet available in your zip code.']
        })

class EditListingTest(TestCase):

    def create_item(self, title="Object Name", description="Object Description"):
        return Item.objects.create(title=title, description=description)

    def create_full_listing(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 100,
            'buy_now_price': 200,
            'zipcode': 30313,
        }, item=item)
        if form.is_valid():
            listing = form.save()
            return listing

    def test_init_with_listing(self):
        listing = self.create_full_listing()
        EditListingForm(listing=listing)

    def test_init_without_listing(self):
        with self.assertRaises(KeyError):
            EditListingForm()

    def test_valid_data(self):
        listing = self.create_full_listing()
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '4',
            'starting_offer': 105,
            'buy_now_price': 205,
            'zipcode': 30309,
        }, listing=listing)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(listing.item.title, 'Different Name')
        self.assertEqual(listing.item.description, 'Different Description')
        self.assertEqual(listing.item.category, '4')
        self.assertEqual(listing.starting_offer, 105)
        self.assertEqual(listing.buy_now_price, 205)
        self.assertEqual(listing.zipcode, 30309)

    def test_invalid_after_first_offer(self):
        listing = self.create_full_listing()
        listing.current_offer = 106
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '4',
            'starting_offer': 105,
            'buy_now_price': 205,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'buy_now_price': ['Buy now price must be at least 10% higher than starting offer, which must be at least '
                              '$5.00'],
            'starting_offer': ['You can\'t edit the starting offer after an offer has been made.']
        })

    def test_invalid_after_first_offer(self):
        listing = self.create_full_listing()
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '4',
            'starting_offer': 4,
            'buy_now_price': 205,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'buy_now_price': ['Buy now price must be at least 10% higher than starting offer, which must be at least '
                              '$5.00'],
            'starting_offer': ['The minimum starting offer is $5.00.']
        })

    def test_invalid_category(self):
        listing = self.create_full_listing()
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '0',
            'starting_offer': 105,
            'buy_now_price': 205,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'category': ['You must choose a category for your item.']
        })

    def test_invalid_buy_now_price(self):
        listing = self.create_full_listing()
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '3',
            'starting_offer': 105,
            'buy_now_price': 105,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'buy_now_price': ['Buy now price must be at least 10% higher than starting offer.']
        })

    def test_invalid_zip_code(self):
        listing = self.create_full_listing()
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '3',
            'starting_offer': 105,
            'buy_now_price': 205,
            'zipcode': 90210,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'zipcode': ['Unfortunately, Circa is not yet available in that zip code.']
        })

class OfferTest(TestCase):

    def create_user(self):
        return User.objects.create_user(username='Juan', password='Pablo')

    def create_item(self, title="Object Name", description="Object Description"):
        seller = User.objects.create_user(username='Circa', password='Seller')
        return Item.objects.create(title=title, description=description, seller=seller)

    def create_full_listing(self):
        item = self.create_item()
        form = ListingForm({
            'starting_offer': 100,
            'buy_now_price': 200,
            'zipcode': 30313,
        }, item=item)
        if form.is_valid():
            listing = form.save()
            return listing

    def test_init_with_user_and_listing(self):
        user = self.create_user()
        listing = self.create_full_listing()
        OfferForm(user=user, listing=listing)

    def test_init_without_input(self):
        with self.assertRaises(KeyError):
            OfferForm()

    def test_valid_data(self):
        user = self.create_user()
        listing = self.create_full_listing()
        form = OfferForm({
            'offer': 100,
            'zipcode': 30313,
        }, user=user, listing=listing)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(listing.current_offer, 100)

    def test_invalid_offer(self):
        user = self.create_user()
        listing = self.create_full_listing()
        form = OfferForm({
            'offer': 95,
            'zipcode': 30313,
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'offer': ['Your offer cannot be less than the asking price.']
        })

    def test_invalid_second_offer(self):
        user = self.create_user()
        listing = self.create_full_listing()
        listing.current_offer = 100
        form = OfferForm({
            'offer': 95,
            'zipcode': 30313,
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'offer': ['Your offer must be greater than the current offer.']
        })

    def test_offer_on_own_item(self):
        listing = self.create_full_listing()
        form = OfferForm({
            'offer': 100,
            'zipcode': 30313,
        }, user=listing.item.seller, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'offer': ['You can\'t submit an offer on your own item.']
        })

    def test_invalid_zipcode(self):
        user = self.create_user()
        listing = self.create_full_listing()
        form = OfferForm({
            'offer': 100,
            'zipcode': 90210,
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'zipcode': ['Unfortunately, Circa is only available in metro Atlanta. Visit our '
                        'help page to see which zipcodes are available.']
        })