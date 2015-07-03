from django.test import LiveServerTestCase
from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import unittest
import time

@override_settings(DEBUG=True, EMAIL_BACKEND="djrill.mail.backends.djrill.DjrillBackend")
class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        time.sleep(3)
        self.browser.quit()

    def test_new_visitor_to_site_non_mobile(self):
        self.browser.maximize_window()
        # Jeremy heard about a new site called usecirca.com and figured he see what all the hub-bub was
        self.browser.get(self.live_server_url)

        # Upon arrival, Jeremy is greeted by a flashy design and a bitchin' logo
        self.assertIn('Circa - Buy and Sell Locally', self.browser.title)
        jumbotron_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Buy and Sell in Atlanta', jumbotron_text)

        # "Wow", exclaims Jeremy, "I need to make an account right-stat-now!"
        # It's at this point that Jeremy navigates to the Sign-up page
        sign_up_button = self.browser.find_element_by_id("sign-up-large")
        sign_up_button.click()

        # Jeremy now sees the form by which he can create an account.  Being savvy to the world,
        # he opts to create an account with email instead of using Facebook
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Sign up for Circa', header_text)

        # Jeremy puts in his information and submits so that he may begin his wonderful journey on Circa
        username_field = self.browser.find_element_by_id('id_username')
        username_field.send_keys('jeremyizkewl')
        email_field = self.browser.find_element_by_id('id_email')
        email_field.send_keys('jeremy@example.com')
        password_field = self.browser.find_element_by_id('id_password1')
        password_field.send_keys('pooploop')
        password_confirm_field = self.browser.find_element_by_id('id_password2')
        password_confirm_field.send_keys('pooploop')
        password_confirm_field.send_keys(Keys.ENTER)

        # Gleefully, Jeremy sees that his new user name is up in the corner and that he is now logged in
        user_button = self.browser.find_element_by_id('username-large')
        user_text = user_button.text
        self.assertIn('jeremyizkewl', user_text)

        # Satisfied that he now has an account in the most important application ever, Jeremy logs out
        # and leaves to go tell his friends about Circa
        user_button.click()
        logout_button = self.browser.find_element_by_id('logout-large')
        logout_button.click()

