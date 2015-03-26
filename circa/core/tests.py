from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from core.models import Item

from core.views import index


class HomePageTests(TestCase):

    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        expected_html = render_to_string('index.html')
        self.assertEqual(response.content.decode(),expected_html)

class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):

        first_item = Item()
        first_item.description = 'Its an SAT, its a tutor, what more do you want?'
        first_item.save()

        second_item = Item()
        second_item.description = 'GYROSCOPES!'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(),2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.description, 'Its an SAT, its a tutor, what more do you want?')
        self.assertEqual(second_saved_item.description, 'GYROSCOPES!')
