from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from core.views import index


class HomePageTests(TestCase):

    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>Circa - Buy and Sell Locally</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))