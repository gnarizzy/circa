from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from core.models import Item
from core.models import Auction
from core.models import UserProfile
from django.contrib.auth.models import User

from core.views import index


class HomePageTests(TestCase):

    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_home_page_lists_items(self):
        auction1 = Auction()
        auction2 = Auction()

        auction1.save()
        auction2.save()

        buyer_1 = User(username = 'First Buyer')
        buyer_1.save()

        buyer_2 = User(username = 'Second Buyer')
        buyer_2.save()

        seller_1 = User(username = 'First Seller')
        seller_1.save()

        seller_2 = User(username = 'Second Seller')
        seller_2.save()

        Item.objects.create(description='A broken laser pointer',auction = auction1, buyer=buyer_1, seller=seller_1)
        Item.objects.create(description='Ten Gallon Hat',auction = auction2, buyer=buyer_2, seller=seller_2)
        response = self.client.get('/')

        self.assertContains(response,'A broken laser pointer')
        self.assertContains(response,'Ten Gallon Hat')
        

class ItemModelTest(TestCase):
# TODO Refactor this
    def test_saving_and_retrieving_items(self):

        auction1 = Auction()
        auction2 = Auction()

        auction1.save()
        auction2.save()

        buyer_1 = User(username = 'First Buyer')
        buyer_1.save()

        buyer_2 = User(username = 'Second Buyer')
        buyer_2.save()


        seller_1 = User(username = 'First Seller')
        seller_1.save()

        seller_2 = User(username = 'Second Seller')
        seller_2.save()

        desc = 'Its an SAT, its a tutor, what more do you want?'
        photo_1 = 'http://someurl.com'
        photo_2 = 'http://someurl2.com'
        photo_3 = 'http://someurl3.com'
        first_item = Item(description = desc, photo1 = photo_1, photo2 = photo_2, photo3 = photo_3, auction = auction1,
                          seller = seller_1, buyer = buyer_1)

        first_item.save()

        second_item = Item(description='GYROSCOPES!', auction=auction2, seller = seller_2, buyer = buyer_2)
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(),2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.description, 'Its an SAT, its a tutor, what more do you want?')
        self.assertEqual(first_saved_item.photo1, 'http://someurl.com')
        self.assertEqual(first_saved_item.photo2, 'http://someurl2.com')
        self.assertEqual(first_saved_item.photo3, 'http://someurl3.com')
        self.assertEqual(first_saved_item.auction, auction1)
        self.assertEqual(first_saved_item.seller, seller_1)
        self.assertEqual(first_saved_item.buyer, buyer_1)
        self.assertEqual(second_saved_item.description, 'GYROSCOPES!')

# TODO Add tests for saving and retrieving other models
# TODO Test one-to-one relations
