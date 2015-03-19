from django.test import TestCase
from django.core.urlresolvers import resolve
from core.views import index


class HomePageTests(TestCase):

    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)