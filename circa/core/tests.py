from core.payout import calc_payout, COMMISSION_BREAKEVEN, COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_MAX
from core.models import Item, Listing, PromoCode, Address, UserProfile
from core.forms import EditListingForm, PromoForm, AddressForm, ItemListingForm
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

    @staticmethod
    def create_user(self):
        return User.objects.create_user(username='JuanPablo', password='superburrito')

    def test_init_with_user(self):
        user = self.create_user(self)
        ItemListingForm(seller=user)

    def test_init_without_user(self):
        with self.assertRaises(KeyError):
            ItemListingForm()

    def test_valid_data(self):
        user = self.create_user(self)
        with open('static/other/test_image.jpg', 'rb') as fp:
            form = ItemListingForm({
                'title': 'Three PS3s',
                'description': 'All your PS3 are belong to us.',
                'category': '1',
                'price': 300,
                'zipcode': 30313,
                'crop_x': 0,
                'crop_y': 0,
                'crop_width': 450,
                'crop_height': 450
            }, {'photo': SimpleUploadedFile(fp.name, fp.read())}, seller=user)
            # self.assertTrue(form.is_valid())
            self.assertTrue(form.is_valid())
            item = form.save()
            self.assertEqual(item.title, 'Three PS3s')
            self.assertEqual(item.category, 1)
            self.assertEqual(item.listing.price, 300)
            self.assertEqual(item.listing.zipcode, 30313)

    def test_invalid_data(self):
        user = self.create_user(self)
        form = ItemListingForm({}, seller=user)
        # self.assertTrue(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['This field is required.'],
            'price': ['This field is required.'],
            'zipcode': ['This field is required.'],
            'crop_x': ['This field is required.'],
            'crop_y': ['This field is required.'],
            'crop_width': ['This field is required.'],
            'crop_height': ['This field is required.'],
            'photo': ['This field is required.']
        })

    def test_invalid_category(self):
        user = self.create_user(self)
        form = ItemListingForm({
            'category': '0'
        }, seller=user)
        # self.assertTrue(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['You must choose a category for your item.'],
            'price': ['This field is required.'],
            'zipcode': ['This field is required.'],
            'crop_x': ['This field is required.'],
            'crop_y': ['This field is required.'],
            'crop_width': ['This field is required.'],
            'crop_height': ['This field is required.'],
            'photo': ['This field is required.']
        })

    def test_out_of_area_zipcode(self):
        user = self.create_user(self)
        form = ItemListingForm({
            'zipcode': 90210
        }, seller=user)
        # self.assertTrue(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['This field is required.'],
            'price': ['This field is required.'],
            'zipcode': ['Unfortunately, Circa is not yet available in that zip code.'],
            'crop_x': ['This field is required.'],
            'crop_y': ['This field is required.'],
            'crop_width': ['This field is required.'],
            'crop_height': ['This field is required.'],
            'photo': ['This field is required.']
        })

    def test_under_priced(self):
        user = self.create_user(self)
        form = ItemListingForm({
            'price': 4
        }, seller=user)
        # self.assertTrue(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'title': ['This field is required.'],
            'description': ['This field is required.'],
            'category': ['This field is required.'],
            'price': ['The minimum price is $5.00.'],
            'zipcode': ['This field is required.'],
            'crop_x': ['This field is required.'],
            'crop_y': ['This field is required.'],
            'crop_width': ['This field is required.'],
            'crop_height': ['This field is required.'],
            'photo': ['This field is required.']
        })


class EditListingTest(TestCase):

    @staticmethod
    def create_item_and_listing(self):
        user = User.objects.create_user(username="frankie", password="blahblahblah")
        item = Item.objects.create(title="Hello Friend", description="This is a test", seller=user)
        listing = Listing.objects.create(price=50, zipcode=30313)
        item.listing = listing
        item.save()
        listing.save()
        return listing

    def test_init_with_listing(self):
        listing = self.create_item_and_listing(self)
        EditListingForm(listing=listing)

    def test_init_without_listing(self):
        with self.assertRaises(KeyError):
            EditListingForm()

    def test_valid_data(self):
        listing = self.create_item_and_listing(self)
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '4',
            'price': 105,
            'zipcode': 30309,
        }, listing=listing)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(listing.item.title, 'Different Name')
        self.assertEqual(listing.item.description, 'Different Description')
        self.assertEqual(listing.item.category, '4')
        self.assertEqual(listing.price, 105)
        self.assertEqual(listing.zipcode, 30309)

    def test_invalid_after_first_offer_2(self):
        listing = self.create_item_and_listing(self)
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '4',
            'price': 4,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'price': ['The minimum price is $5.00.']
        })

    def test_invalid_category(self):
        listing = self.create_item_and_listing(self)
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '0',
            'price': 105,
            'zipcode': 30309,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'category': ['You must choose a category for your item.']
        })

    def test_invalid_zip_code(self):
        listing = self.create_item_and_listing(self)
        form = EditListingForm({
            'title': 'Different Name',
            'description': 'Different Description',
            'category': '3',
            'price': 105,
            'zipcode': 90210,
        }, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'zipcode': ['Unfortunately, Circa is not yet available in that zip code.']
        })


class PromoTest(TestCase):

    @staticmethod
    def create_item_and_listing(self):
        user = User.objects.create_user(username="frankie", password="blahblahblah")
        item = Item.objects.create(title="Hello Friend", description="This is a test", seller=user)
        listing = Listing.objects.create(price=50, zipcode=30313)
        item.listing = listing
        item.save()
        listing.save()
        return listing

    @staticmethod
    def create_promo_code(self, user):
        return PromoCode.objects.create(user=user, code='12345', value='5')

    @staticmethod
    def create_user(self, username="dickbutt", password="ttubkicd"):
        return User.objects.create_user(username=username, password=password)

    def test_init_with_user(self):
        user = self.create_user(self)
        listing = self.create_item_and_listing(self)
        PromoForm(user=user, listing=listing)

    def test_init_without_input(self):
        with self.assertRaises(KeyError):
            PromoForm()

    def test_valid_data(self):
        user = self.create_user(self)
        listing = self.create_item_and_listing(self)
        promo = self.create_promo_code(self, user)
        form = PromoForm({
            'code': '12345'
        }, user=user, listing=listing)
        self.assertTrue(form.is_valid())
        form.save()
        promo = PromoCode.objects.get(pk=promo.id)
        self.assertEqual(promo.listing.id, listing.id)

    def test_invalid_code(self):
        user = self.create_user(self)
        listing = self.create_item_and_listing(self)
        self.create_promo_code(self, user)
        form = PromoForm({
            'code': '12344'
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that code is not valid.']
        })

    def test_used_code(self):
        user = self.create_user(self)
        listing = self.create_item_and_listing(self)
        promo = self.create_promo_code(self, user)
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
        user = self.create_user(self)
        listing = self.create_item_and_listing(self)
        form = PromoForm({
            'code': '12345'
        }, user=user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that code isn\'t valid.']
        })

    def test_invalid_user(self):
        user = self.create_user(self)
        invalid_user = self.create_user(self, 'Jeff', 'Goldblum')
        listing = self.create_item_and_listing(self)
        self.create_promo_code(self, user)
        form = PromoForm({
            'code': '12345'
        }, user=invalid_user, listing=listing)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'code': ['Sorry, that\'s not your code!']
        })


class AddressTest(TestCase):

    @staticmethod
    def create_user(self):
        return User.objects.create_user(username='Spongebob', password='Squarepants')

    @staticmethod
    def create_address(self):
        return Address.objects.create(
            address_line_1='111 Ur Mum',
            city='Buttville',
            state='GA',
            zipcode='30313'
        )

    def test_address_creation(self):
        address = self.create_address(self)

        self.assertTrue(isinstance(address, Address))
        self.assertEqual("111 Ur Mum", address.__str__())

    def test_init_with_user(self):
        user = self.create_user(self)
        AddressForm(user=user)

    def test_init_without_user(self):
        with self.assertRaises(KeyError):
            AddressForm()

    def test_with_valid_data(self):
        user = self.create_user(self)
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
        user = self.create_user(self)
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


#slug tests
#1) correct id but incorrect slug redirects to correct slugified url (/listing/40/asdas redirects to /listing/40/actual-slug)
#2) correct id but no slug redirects to slugified url, (/listing/40/ redirects to /listing/40/actual-slug)
#3) correct slug--slug = slugify(item.title)(uses django.utils.text slugify method)
