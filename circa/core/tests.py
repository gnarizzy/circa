from core.payout import calc_payout, COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_MAX
from core.models import Item, Listing, PromoCode, Address, UserProfile
from core.forms import ItemForm, ListingForm, EditListingForm, OfferForm, PromoForm, AddressForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from decimal import *


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


class ItemListingTest(TestCase):
    pass


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

    def test_invalid_after_first_offer_2(self):
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


class PromoTest(TestCase):

    def create_user(self, username='Juan', password='Pablo'):
        return User.objects.create_user(username=username, password=password)

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

    def create_promo_code(self, user):
        return PromoCode.objects.create(user=user, code='12345', value='5')

    def test_init_with_user(self):
        user = self.create_user()
        listing = self.create_full_listing()
        PromoForm(user=user, listing=listing)

    def test_init_without_input(self):
        with self.assertRaises(KeyError):
            PromoForm()

    def test_valid_data(self):
        user = self.create_user()
        listing = self.create_full_listing()
        promo = self.create_promo_code(user)
        form = PromoForm({
            'code': '12345'
        }, user=user, listing=listing)
        self.assertTrue(form.is_valid())
        form.save()
        promo = PromoCode.objects.get(pk=promo.id)
        self.assertEqual(listing.discount, 5)
        self.assertEqual(promo.redeemed, True)

    def test_invalid_code(self):
        user = self.create_user()
        listing = self.create_full_listing()
        self.create_promo_code(user)
        form = PromoForm({
            'code': '12344'
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that code is not valid.']
        })

    def test_used_code(self):
        user = self.create_user()
        listing = self.create_full_listing()
        promo = self.create_promo_code(user)
        promo.redeemed = True
        promo.save()
        form = PromoForm({
            'code': '12345'
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, promo code already used.']
        })

    def test_edge_case_with_no_promo_codes(self):
        user = self.create_user()
        listing = self.create_full_listing()
        form = PromoForm({
            'code': '12345'
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that code isn\'t valid.']
        })

    def test_invalid_user(self):
        user = self.create_user()
        invalid_user = self.create_user('Jeff', 'Goldblum')
        listing = self.create_full_listing()
        self.create_promo_code(user)
        form = PromoForm({
            'code': '12345'
        }, user=invalid_user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that\'s not your code!']
        })


class AddressTest(TestCase):

    def create_user(self):
        return User.objects.create_user(username='Spongebob', password='Squarepants')

    def create_address(self):
        return Address.objects.create(
            address_line_1='111 Ur Mum',
            city='Buttville',
            state='GA',
            zipcode='30313'
        )

    def test_address_creation(self):
        address = self.create_address()

        self.assertTrue(isinstance(address, Address))
        self.assertEqual("111 Ur Mum", address.__str__())

    def test_init_with_user(self):
        user = self.create_user()
        AddressForm(user=user)

    def test_init_without_user(self):
        with self.assertRaises(KeyError):
            AddressForm()

    def test_with_valid_data(self):
        user = self.create_user()
        form = AddressForm({
            'address_line_1': '555 Five ave',
            'address_line_2': '',
            'city': 'Alpharetta',
            'state': 'GA',
            'zipcode': '30009',
            'special_instructions': 'Don\'t drop it!'
        }, user=user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(user.userprofile.address.address_line_1, '555 Five ave')
        self.assertEqual(user.userprofile.address.address_line_2, '')
        self.assertEqual(user.userprofile.address.city, 'Alpharetta')
        self.assertEqual(user.userprofile.address.state, 'GA')
        self.assertEqual(user.userprofile.address.zipcode, '30009')
        self.assertEqual(user.userprofile.address.special_instructions, 'Don\'t drop it!')

    def test_with_missing_data(self):
        user = self.create_user()
        form = AddressForm({
            'address_line_1': '555 Five ave',
            'address_line_2': '',
            'state': 'GA',
            'zipcode': '30009',
            'special_instructions': 'Don\'t drop it!'
        }, user=user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'city': ['This field is required.']
        })
