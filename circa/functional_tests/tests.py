from core.models import PromoCode, User, Listing
from core.payout import calc_payout
from datetime import datetime
from django.core import mail
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import os
import time


@override_settings(DEBUG=True)
class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
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
        header_text = self.browser.find_element_by_id('sign-up-header').text
        self.assertIn('Sign up for Circa', header_text)

        self.browser.find_element_by_id("show-sign-up").click()

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

        time.sleep(5)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to Circa!")

        # Gleefully, Jeremy sees that his new user name is up in the corner and that he is now logged in
        user_button = self.browser.find_element_by_id('username-large')
        user_text = user_button.text
        self.assertIn('jeremyizkewl', user_text)

        # Now that he has an account, Jeremy wanted to post something and see if he could make a quick buck
        sell_button = self.browser.find_element_by_id('sell-large')
        sell_button.click()
        sell_header_text = self.browser.find_element_by_id('sell-page-header').text
        self.assertIn('List an item for sale', sell_header_text)

        # After searching through his old knick-knacks, Jeremy finds the perfect item to sell
        title_field = self.browser.find_element_by_id('id_title')
        title_field.send_keys('Dragon Slaying Sword')
        description_field = self.browser.find_element_by_id('id_description')
        description_field.send_keys('Lightly used, originally bought at a garage sale.  Can\'t confirm if it actually '
                                    'offers protection from a dragan.')
        category_field = Select(self.browser.find_element_by_id('id_category'))
        category_field.select_by_value('5')
        photo_field = self.browser.find_element_by_id('id_photo')
        photo_field.send_keys(os.getcwd() + '\\functional_tests\\func_test_image.jpg')

        # Because of his 1337 haxor skillz, Jeremy inputs his desired cropping manually
        self.browser.execute_script("document.getElementById('id_crop_x').style.display = 'inline';")
        self.browser.execute_script("document.getElementById('id_crop_y').style.display = 'inline';")
        self.browser.execute_script("document.getElementById('id_crop_width').style.display = 'inline';")
        self.browser.execute_script("document.getElementById('id_crop_height').style.display = 'inline';")
        self.browser.find_element_by_id('id_crop_x').send_keys(0)
        self.browser.find_element_by_id('id_crop_y').send_keys(0)
        self.browser.find_element_by_id('id_crop_width').send_keys(450)
        self.browser.find_element_by_id('id_crop_height').send_keys(450)

        price_field = self.browser.find_element_by_id('id_price')
        price_field.send_keys('50')
        zip_field = self.browser.find_element_by_id('id_zipcode')
        zip_field.send_keys('30313')
        self.browser.find_element_by_id('list-item-button').click()

        # Alas, all his hard work paid off and Jeremy beheld his post in all its glory
        listing_title_text = self.browser.find_element_by_id('listing-title').text
        self.assertIn('Dragon Slaying Sword', listing_title_text)

        # Having had adequate time to behold his handy work, Jeremy heads back to the home page
        logo_button = self.browser.find_element_by_id('logo')
        logo_button.click()

        # From the home page, Jeremy can clearly see his new post and is hopeful that somebody buys it soon
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Dragon Slaying Sword', page_text)

        # Satisfied that he now has an account and has posted his item, Jeremy logs out of Circa and sprints
        # to the door, anxious to tell his friends of his new find
        user_button = self.browser.find_element_by_id('username-large')
        user_button.click()
        logout_button = self.browser.find_element_by_id('logout-large')
        logout_button.click()
        jumbotron_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Buy and Sell in Atlanta', jumbotron_text)

        # A while later, Jeremy returns to see how his item postage is going.  He clicks on his post.
        listing_card = self.browser.find_element_by_id('1')
        listing_card.click()

        # When redirected, he notices he made a typo!  Quickly, Jeremy logs in to rectify his mistake
        login_in_button = self.browser.find_element_by_id('login-large')
        login_in_button.click()

        username_field = self.browser.find_element_by_id('id_username')
        username_field.send_keys('jeremyizkewl')
        password_field = self.browser.find_element_by_id('id_password')
        password_field.send_keys('pooploop')
        password_field.send_keys(Keys.ENTER)

        # After logging in, Jeremy navigates to the listing page and then clicks to edit the page
        listing_card = self.browser.find_element_by_id('1')
        listing_card.click()

        edit_button = self.browser.find_element_by_id('edit')
        edit_button.click()

        edit_description = self.browser.find_element_by_id('id_description')
        edit_description.send_keys(Keys.BACKSPACE)
        edit_description.send_keys(Keys.BACKSPACE)
        edit_description.send_keys(Keys.BACKSPACE)
        edit_description.send_keys('on.')

        update_listing_button = self.browser.find_element_by_id('update-listing')
        update_listing_button.click()

        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('from a dragon.', page_text)

        # Now satisfied that his mistake has been resolved, Jeremy again logs out and goes on to do whatever
        # it is that Jeremy does in his spare time
        user_button = self.browser.find_element_by_id('username-large')
        user_button.click()
        logout_button = self.browser.find_element_by_id('logout-large')
        logout_button.click()
        jumbotron_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Buy and Sell in Atlanta', jumbotron_text)

        # Later, a new person visits the site and makes an account.  Her name is Abigail
        sign_up_button = self.browser.find_element_by_id("sign-up-large")
        sign_up_button.click()

        header_text = self.browser.find_element_by_id('sign-up-header').text
        self.assertIn('Sign up for Circa', header_text)

        self.browser.find_element_by_id("show-sign-up").click()

        # She inputs her information and then proceeds to login
        username_field = self.browser.find_element_by_id('id_username')
        username_field.send_keys('samiam')
        email_field = self.browser.find_element_by_id('id_email')
        email_field.send_keys('samantha@example.com')
        password_field = self.browser.find_element_by_id('id_password1')
        password_field.send_keys('zoopzoopzoop')
        password_confirm_field = self.browser.find_element_by_id('id_password2')
        password_confirm_field.send_keys('zoopzoopzoop')
        password_confirm_field.send_keys(Keys.ENTER)

        # An email verifies her new account
        time.sleep(5)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Welcome to Circa!")

        # The first thing she notices is a neat sword on the front page.  She immediately clicks it.
        listing_card = self.browser.find_element_by_id('1')
        listing_card.click()

        # This is just what she's been looking for to add to her collection!  She immediately buys it
        buy_button = self.browser.find_element_by_id('buy-item')
        buy_button.click()

        # Because Stripe is a b***h to get working on a functional test, I'm just making the item paid for in the
        # background
        listing = Listing.objects.all()[0]
        listing.item.buyer = User.objects.get(pk=2)
        listing.item.save()
        listing.end_date = datetime.now()
        listing.paid_for = True
        listing.payout = calc_payout(listing.price)
        listing.save()

        # Now that she has "paid" for her item, she is redirected to input her address
        self.browser.get(self.live_server_url + '/address/?next=/confirm/' + str(listing.id))

        address_line_1 = self.browser.find_element_by_id('id_address_line_1')
        address_line_1.send_keys('454 Pine Grove Ln')
        city = self.browser.find_element_by_id('id_city')
        city.send_keys('Atlanta')
        zipcode = self.browser.find_element_by_id('id_zipcode')
        zipcode.send_keys('30313')
        special_instructions = self.browser.find_element_by_id('id_special_instructions')
        special_instructions.send_keys('Leave it under the door mat.')
        special_instructions.send_keys(Keys.ENTER)

        # Now that she has inputted her address, she is asked to confirm, and then an email is sent
        # to all parties involved to get the ball rolling
        confirm_addr_text = self.browser.find_element_by_id('confirm-address').text
        self.assertEqual('Confirm your address', confirm_addr_text)

        confirm_button = self.browser.find_element_by_id('confirm-button')
        confirm_button.click()

        time.sleep(5)
        self.assertEqual(len(mail.outbox), 5)
        self.assertEqual(mail.outbox[2].subject, "You've bought Dragon Slaying Sword")
        self.assertEqual(mail.outbox[3].subject, "Dragon Slaying Sword has sold!")
        self.assertEqual(mail.outbox[4].subject, "Pending Delivery")

        # Redirected to the Success page, Abigail knows her sale is in good hands
        success_header = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Success', success_header)
