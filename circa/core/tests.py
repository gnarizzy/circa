from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase, Client
from django.utils import timezone

from core.forms import ItemForm
from core.models import Item, Auction, UserProfile
from core.views import index, sell, create_auction, auction_detail

from datetime import timedelta

class HomePageTests(TestCase):

    def add_auctions(self):
        auction1 = Auction.objects.create()
        auction2 = Auction.objects.create()
        buyer_1 = User.objects.create_user(username='First Buyer')
        buyer_2 = User.objects.create_user(username='Second Buyer')
        seller_1 = User.objects.create_user(username='First Seller')
        seller_2 = User.objects.create_user(username='Second Seller')
        item_1=Item.objects.create(
            title='Broken laser pointer',
            description='This thing is broken and useless',
            auction = auction1,
            buyer=buyer_1,
            seller=seller_1
        )
        item_2=Item.objects.create(
            title='Ten Gallon Hat',
            description='If people shoot at you, they will miss',
            auction = auction2,
            buyer=buyer_2,
            seller=seller_2
        )

    def add_expired_auction(self):
        expired_auction = Auction.objects.create(end_date=timezone.now() - timedelta(days=1))
        winning_buyer = User.objects.create_user(username='Frankendoodle')
        lucky_seller = User.objects.create_user(username='Spongebob')
        Item.objects.create(
            title='Giant magical pencil',
            description='\"You doodle, me Spongebob\"',
            auction = expired_auction,
            buyer=winning_buyer,
            seller=lucky_seller
        )

    def add_item_without_auction(self):
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
        self.add_auctions()
        response = self.client.get('/')

        self.assertContains(response,'Broken laser pointer')
        self.assertContains(response,'Ten Gallon Hat')
        self.assertNotContains(response, 'This is awkward...there\'s nothing for sale!')

    def test_home_page_does_not_list_auctions_that_have_ended(self):
        self.add_auctions()
        response = self.client.get('/')

        self.assertNotContains(response, 'Giant magical pencil')

    def test_home_page_does_not_list_items_with_no_auction(self):
        self.add_auctions()
        self.add_item_without_auction()
        response = self.client.get('/')

        self.assertNotContains(response, 'Schrute Bucks')

    #test ordering by soonest auction end date ***Andrew Note: This would probably be a functional test***

class ModelTest(TestCase):

    def add_items(self):
        auction_1 = Auction.objects.create
        seller = User.objects.create_user(username='Breadface')
        Item.objects.create(
            title='An old, crappy laptop',
            description='Water has been spilled on it, so the key board doesn\'t work',
            photo='http://localhost:8000/picture',
            seller=seller
        )
        Item.objects.create(
            title='A joystick that no one wants',
            description=':-(',
            photo='http://localhost:8000/picture2',
            seller=seller
        )

    def test_saving_and_retrieving_items(self):
        self.add_items()

        saved_item = Item.objects.first()

        self.assertEqual(Item.objects.all().count(), 2)
        self.assertEqual(saved_item.title, 'An old, crappy laptop')
        self.assertEqual(saved_item.seller.username, 'Breadface')
        self.assertEqual(saved_item.auction, None)

# class ItemModelTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#
# # TODO change photo urls to actual files and test accordingly
# # TODO Refactor this
#     def test_saving_and_retrieving_items(self):
#
#         auction1 = Auction()
#         auction2 = Auction()
#
#         auction1.save()
#         auction2.save()
#
#         buyer_1 = User(username = 'First Buyer')
#         buyer_1.save()
#
#         buyer_2 = User(username = 'Second Buyer')
#         buyer_2.save()
#
#
#         seller_1 = User(username = 'First Seller')
#         seller_1.save()
#
#         seller_2 = User(username = 'Second Seller')
#         seller_2.save()
#
#         desc = 'Its an SAT, its a tutor, what more do you want?'
#         photo_1 = 'http://someurl.com'
#         first_item = Item(description = desc, photo = photo_1, auction = auction1,
#                           seller = seller_1, buyer = buyer_1)
#
#         first_item.save()
#
#         second_item = Item(description='GYROSCOPES!', auction=auction2, seller = seller_2, buyer = buyer_2)
#         second_item.save()
#
#         saved_items = Item.objects.all()
#         self.assertEqual(saved_items.count(),2)
#
#         first_saved_item = saved_items[0]
#         second_saved_item = saved_items[1]
#
#         self.assertEqual(first_saved_item.description, 'Its an SAT, its a tutor, what more do you want?')
#         self.assertEqual(first_saved_item.photo, 'http://someurl.com')
#         self.assertEqual(first_saved_item.auction, auction1)
#         self.assertEqual(first_saved_item.seller, seller_1)
#         self.assertEqual(first_saved_item.buyer, buyer_1)
#         self.assertEqual(second_saved_item.description, 'GYROSCOPES!')
#
# # TODO Add tests for saving and retrieving other models
# # TODO Test one-to-one relations
# # TODO Test form stuff
# # TODO Investigate two urls.py
#
# class PostItemTest(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#
#     def test_sell_url_resolves_to_sell_view(self):
#         found = resolve('/sell/')
#         self.assertEqual(found.func, sell)
#
#     def test_sell_page_renders_sell_template(self):
#         response = self.client.get('/sell/')
#         self.assertTemplateUsed(response, 'sell.html')
#
#     def test_sell_page_uses_item_form(self):
#         response = self.client.get('/sell/')
#
#         # I don't think this is being checked correctly
#         self.assertIsInstance(response.context['form'], ItemForm)

#may be helpful for writing form tests! http://www.effectivedjango.com/forms.html

    #def_test_form_submission_results_in_new_item_on_home_page(self):

    #def_test_redirect_after_successful_form_submission(self):

    # TODO test form validation?

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
#         self.assertTemplateUsed(response, 'create_auction.html')

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

#test that signup defaults to redirecting to home page

#test that sign up from required login flow redirects to original page

#test that logout redirets to home page

#Test signup link disappears after login

#Test all the stripe stuff, from json to template and all the tests stripe lists on their site, test declined cards,
#test creating users, test notifications after purchase is made

#test success page, help page

#auction_ending_test (can't bid on item, appropriate text, message if user hasn't paid yet, message if user has paid,  etc.)

#test to make sure POST cant be submitted to auction that has ended

#transactional email tests-- outbid, payment complete, delivered, reminder to pay

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

#403 tests