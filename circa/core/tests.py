from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils import timezone

from core.forms import ItemForm
from core.models import Item, Listing, UserProfile
from core.views import index, sell, create_listing, listing_detail

from datetime import timedelta

class HomePageTests(TestCase):

    def add_listings(self):
        listing1 = Listing.objects.create()
        listing2 = Listing.objects.create()
        buyer_1 = User.objects.create_user(username='First Buyer')
        buyer_2 = User.objects.create_user(username='Second Buyer')
        seller_1 = User.objects.create_user(username='First Seller')
        seller_2 = User.objects.create_user(username='Second Seller')
        item_1=Item.objects.create(
            title='Broken laser pointer',
            description='This thing is broken and useless',
            listing = listing1,
            buyer=buyer_1,
            seller=seller_1
        )
        item_2=Item.objects.create(
            title='Ten Gallon Hat',
            description='If people shoot at you, they will miss',
            listing = listing2,
            buyer=buyer_2,
            seller=seller_2
        )

    def add_expired_listing(self):
        expired_listing = Listing.objects.create(end_date=timezone.now() - timedelta(days=1))
        winning_buyer = User.objects.create_user(username='Frankendoodle')
        lucky_seller = User.objects.create_user(username='Spongebob')
        Item.objects.create(
            title='Giant magical pencil',
            description='\"You doodle, me Spongebob\"',
            listing = expired_listing,
            buyer=winning_buyer,
            seller=lucky_seller
        )

    def add_item_without_listing(self):
        buyer = User.objects.create_user(username='Dwight')
        seller = User.objects.create_user(username='Stanley')
        Item.objects.create(
            title='Schrute Bucks',
            description='Conversion rate of Shrute Bucks to Stanley Nickels is 1:1000',
            buyer=buyer,
            seller=seller
        )

    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_home_page_renders_index_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_home_page_displays_correct_message_with_no_items(self):
        response = self.client.get('/')
        self.assertContains(response, 'This is awkward...there\'s nothing for sale!')

    def test_home_page_lists_items(self):
        self.add_listings()
        response = self.client.get('/')

        self.assertContains(response,'Broken laser pointer')
        self.assertContains(response,'Ten Gallon Hat')
        self.assertNotContains(response, 'This is awkward...there\'s nothing for sale!')

    def test_home_page_does_not_list_listings_that_have_ended(self):
        self.add_listings()
        self.add_expired_listing()
        response = self.client.get('/')

        self.assertNotContains(response, 'Giant magical pencil')

    def test_home_page_does_not_list_items_with_no_listing(self):
        self.add_listings()
        self.add_item_without_listing()
        response = self.client.get('/')

        self.assertNotContains(response, 'Schrute Bucks')

    # test ordering by soonest listing end date ***Andrew Note: This would probably be a functional test***

class SellPageTest(TestCase):

    def auth_user(self):
        User.objects.create_user(username='Juan', password='Pablo')
        self.client.post('/accounts/login/', {'username': 'Juan', 'password': 'Pablo'})

    def create_item(self):
        with open('static/other/test_image.jpg','rb') as fp:
            response = self.client.post(
                '/sell/',
                {'title': 'Crap',
                 'description': 'In a bucket',
                 'photo': fp}
            )

    def test_sell_url_resolves_to_sell_view(self):
        found = resolve('/sell/')
        self.assertEqual(found.func, sell)

    def test_sell_page_redirects_to_login_when_unauthenticated(self):
        response = self.client.get('/sell/')
        self.assertRedirects(response, '/accounts/login/?next=/sell/')

    def test_sell_page_renders_sell_view_when_authenticated(self):
        self.auth_user()
        response = self.client.get('/sell/')
        self.assertTemplateUsed(response, 'sell.html')

    def test_fields_cannot_be_empty(self):
        self.auth_user()
        # this is intentionally missing a photo attachement
        response = self.client.post('/sell/', {'title': 'Crap', 'description': 'In a bucket'})

        self.assertContains(response, 'This field is required.')

    def test_valid_item_submission_goes_to_createlisting(self):
        self.auth_user()
        with open('static/other/test_image.jpg','rb') as fp:
            response = self.client.post(
                '/sell/',
                {'title': 'Crap',
                 'description': 'In a bucket',
                 'photo': fp}
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/createlisting/1', response.url)

    def test_valid_item_submission_creates_item(self):
        self.auth_user()
        self.create_item()

        all_items = Item.objects.all()
        user = User.objects.first()

        self.assertEqual(all_items.count(), 1)
        self.assertEqual(all_items[0].title, 'Crap')
        self.assertEqual(all_items[0].seller, user)

class ModelTest(TestCase):

    def add_items(self):
        listing_1 = Listing.objects.create()
        listing_2 = Listing.objects.create()
        seller = User.objects.create_user(username='Breadface')
        buyer = User.objects.create_user(username='ClumpOfHair')
        Item.objects.create(
            title='An old, crappy laptop',
            description='Water has been spilled on it, so the key board doesn\'t work',
            photo='http://localhost:8000/picture',
            seller=seller,
            buyer=buyer,
            listing=listing_1
        )
        Item.objects.create(
            title='A joystick that no one wants',
            description=':-(',
            photo='http://localhost:8000/picture2',
            seller=seller,
            listing=listing_2
        )

    def listing_integrity_issue(self):
        with transaction.atomic():  # Tester's note: This prevents TransactionManagementErrors
            overly_enthusiastic_listing = Listing.objects.create()
            cheatsy_seller = User.objects.create_user(username='ClumpOfHair')
            Item.objects.create(
                title='An old, crappy laptop',
                description='Water has been spilled on it, so the key board doesn\'t work',
                photo='http://localhost:8000/picture',
                seller=cheatsy_seller,
                listing=overly_enthusiastic_listing
            )
        with transaction.atomic():
            Item.objects.create(
                title='A joystick that no one wants',
                description=':-(',
                photo='http://localhost:8000/picture2',
                seller=cheatsy_seller,
                listing=overly_enthusiastic_listing
            )

    def buyer_seller_integrity_issue(self):
        with transaction.atomic():  # Tester's note: This prevents TransactionManagementErrors
            listing = Listing.objects.create()
            remorseful_seller = User.objects.create_user(username='ClumpOfHair')
            Item.objects.create(
                title='An old, crappy laptop',
                description='Water has been spilled on it, so the key board doesn\'t work',
                photo='http://localhost:8000/picture',
                seller=remorseful_seller,
                buyer=remorseful_seller,
                listing=listing
            )

    # TODO revisit when alt_id is established
    # def user_profile_integrity_issue(self):
    #     with transaction.atomic():  # Tester's note: This prevents TransactionManagementErrors
    #         two_faced_user = User.objects.create_user(username='ShiftySteve')
    #         UserProfile.objects.create(user=two_faced_user)
    #     with transaction.atomic():
    #         UserProfile.objects.create(user=two_faced_user)

    def test_saving_and_retrieving_items(self):
        self.add_items()

        saved_items = Item.objects.all()

        item_1 = saved_items[0]
        item_2 = saved_items[1]

        self.assertEqual(saved_items.count(), 2)
        self.assertEqual(item_1.title, 'An old, crappy laptop')
        self.assertEqual(item_1.seller.username, 'Breadface')
        self.assertIsNone(item_2.buyer)

    def test_listing_to_item_is_one_to_one(self):
        try:
            self.listing_integrity_issue()
        except IntegrityError:
            saved_items = Item.objects.all()

            self.assertEqual(saved_items.count(), 1)
        else:
            self.fail('The Listing/Item relationship is not one-to-one')

    def test_seller_cannot_buy_own_item(self):
        try:
            self.buyer_seller_integrity_issue()
        except IntegrityError:
            saved_items = Item.objects.all()

            self.assertEqual(saved_items.count(), 0)
        else:
            self.fail('The seller can also be the buyer')

    # TODO: Promocode test
    #test that it is actually created with correct values, associated with correct user
    #test that it actually reduces amount, that it can't be used on multiple items
    #test for proper error message for expired code
    #test no charge for $.31 cents or less.


    # TODO revisit when alt_id is established
    # def test_userprofile_is_unique_to_user(self):
    #     try:
    #         self.user_profile_integrity_issue()
    #     except IntegrityError:
    #         userprofiles = UserProfile.objects.all()
    #
    #         self.assertEqual(userprofiles.count(), 1)
    #     else:
    #         self.fail('A User can be mapped to more than one UserProfile')


# TODO Test form stuff
# TODO Investigate two urls.py

#may be helpful for writing form tests! http://www.effectivedjango.com/forms.html

    #def_test_form_submission_results_in_new_item_on_home_page(self):

    #def_test_redirect_after_successful_form_submission(self):

    # test form validation?

# class CreateAuctionTest(TestCase):
#
#     def setUp(self):
#         auction = Auction()
#         auction.save()
#
#         desc = "Potato cannon"
#         photo_1 = "http://potatocannon.com"
#         seller_1 = User(username = "greg")
#         seller_1.save()
#
#         item = Item(description = desc, photo = photo_1,
#                           seller = seller_1)
#         item.save()
#
#         self.client = Client()
#
#     # TODO I believe this is currently mislabeled
#     def test_auction_url_resolves_to_create_auction_view(self):
#         found = resolve('/auction/0/')
#         self.assertEqual(found.func, auction_detail)
#
#     # TODO I also believe this is currently mislabeled
#     def test_auction_page_renders_auction_template(self):
#         response = self.client.get('/createauction/0/')
#         self.assertTemplateUsed(response, 'create_listing.html')

    #def test_auction_cant_be_recreated_after_its_created(self):

    #def test_redirect_after_successful_form_submission(self):

    #def test_error_thrown_if_negative_initial_bid_entered(self):

    #def test_error_thrown_if_negative_buy_now_price_entered(self):

    #def test_error_thrown_if_invalid_seller_zip_code_is_entered(self):

#class AuctionDetailTest(TestCase):

    #def test_auction_detail_url_resolves_to_auction_view(self):

    #def test_auction_detail_page_has_information_for_correct_item(self):

    #def test_auction_detail_page_displays_correct_remaining_auction_time(self):

    #def test_auction_detail_page_renders_auction_detail_template(self):

#class BidTest(TestCase):

    #def test_bids_less_than_or_equal_to_current_bid_throw_validation_error(self):

    #def test_valid_bid_updates_current_bid_on_page(self):

    #def test_valid_bid_includes_success_message_on_page(self):

    #def test_bid_within_10_percent_of_buy_now_price_increases_buy_now_price(self):

    #def test_bid_only_valid_if_buyer_zip_code_is_valid(self):

    #def test_error_message_if_invalid_ziocode

#class AuctionEndTest(TestCase):

    #def test_appropriate_text_on_auction_detail_page_when_auction_ends(self):

    #def test_appropriate_text_on_auction_detail_page_when_user_buys_now(self):

    #def test_notify_winning_bidder_on_auction_end(self):

#class PaymentTest(TestCase):

#class PickupTest(TestCase):

#class RegistrationTest(TestCase):

#class LoginTest(TestCase):

    #def test_after_login_redirected_to_previous_page(self):

#class ListItemTest(TestCase):

    #def test_item_listed_is_associated_with_current_user

    #def test_auction_is_associated_with_correct_user

#class AuthenticationTest(TestCase):

    #def test_unauthenticated_user_cant_sell_item

    #def test_unauthentiated_user_cant_go_to_specific_create_auction_page

    #def test_wrong_user_cant_go_to_specific_create_auction_page

#test that user can bid on multiple items

#test that sller can post multiple items

#test highest bidder is show highest bidder message

#test that people cant bid on own items

#test that sign up defaults to redirecting to home page

#test that unique usernames AND unique email addresses are enforced

#test that sign up from required login flow redirects to original page

#test that logout redirets to home page

#Test signup link disappears after login

#Test all the stripe stuff, from json to template and all the tests stripe lists on their site, test declined cards,
#test creating users, test notifications after purchase is made

#test success page, help page

#auction_ending_test (can't bid on item, appropriate text, message if user hasn't paid yet, message if user has paid,  etc.)

#test to make sure POST cant be submitted to auction that has ended

#transactional email tests-- outbid, payment complete, delivered, reminder to pay, seller notified when listing ends,
#seller notified if item sells

#create deliveries, delivery object

#payment flow test (pay rendersw correct template, requires login, shows correct pending payments [both one or multiple])

#auction_pay test (correct template, correct item, check for correct user and raise error if incorrect user, actually takes payment,
#updates buyer and seller on item, updates paid field on auction, expired if already paid for).

#test if after item bought redirected to /pay/

#test /connect renders correct template, requires login, has apprpriate response based onwhether they've already  connected,
#responds appropriately if they have already connected, if they fail to authorize connection, if they give the wrong authorization scope

#test that appprpriate measures takes place if Stripe connection is revoked, state token for security

#test than transfers to seller accounts are proprerly associated with teh purchase of their item

#test refuns of all aspects of the process

#test Stripe receipt confirmation

#403 tests (they come at appropriate times, basically)

#expired page tests

#test that Facebook login works

#test that proper error message comes up if no email address is given

#test that things don't blow up if facebook email is already in server--maybe try to merge accounts by prompting user?

#test password reset

#test force unique email addresses and usernames

#dashboard tests (Correct number of items for each icon, correct links for each icon)

#background tasks tests

#cant offer below asking price

#mandrill tests for correct amount

#test that preopulated amount is always $1 more than current offer, unless no offers have been made in which case it is
#the asking price