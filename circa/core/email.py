# A helper module to generate emails and avoid spaghetti code
from background_task import background
from circa.settings import ALLOWED_HOSTS
from django.core.mail import EmailMessage
from core.models import User, Listing
from decimal import *
import datetime


OFFER_DENIED = "Hey {},\n\nUnfortunately, your offer is no longer the highest on {}. The current offer is ${} and " \
               "you have 1 hour to make a higher offer. If you don't want to this to happen again, you can buy the " \
               "item now for ${}.\n\nThe listing can be found here: {}\n\nThanks for using Circa, and feel free to " \
               "reply to this email with any questions or feedback." \
               "\n\nSincerely,\n\nThe Circa Team"

LOST_LISTING = "Hey {},\n\nUnfortunately, someone has used the buy now option on {}, which has ended all active " \
               "offers. To avoid this in future listings, you can click \"Buy Now\" to pay for the item immediately " \
               "and guarantee that you'll get it 24 hours.\n\nThanks for using Circa, and feel free to reply to this " \
               "email with any questions or feedback." \
               "\n\nSincerely,\n\nThe Circa Team"

OFFER_ACCEPTED = "Dear {},\n\nYour offer on {} has been accepted!  Please navigate to " \
                 "http://www.usecirca.com/pending/ to pay for your item.  Once paid for, the item will be delivered " \
                 "within 24 hours of the seller handing it off to us.\n\nThanks for being awesome and using Circa!  " \
                 "Feel free to reply with any feedback on how your experience was.  We want to create the best way " \
                 "for students to buy and sell electronics." \
                 "\n\nSincerely,\n\nThe Circa Team"

ITEM_SOLD = "Dear {},\n\nYour item, {}, has sold!  Your total earnings for this sale are ${}, which will be given " \
            "to you upon pick up of the item.\n\nThank you for using Circa!  If you have any feedback on your " \
            "experience, please reply to this email and let us know.  We want to be the best way for students to buy " \
            "and sell electronics locally." \
            "\n\nSincerely\n\nThe Circa Team"

LISTING_BUY_NOW = "Hello,\n\nCongratulations on getting the {}! This email is to confirm that you paid ${} for this " \
                  "item.  Can you reply with your address and preferred delivery time? Your item will be delivered " \
                  "within 24 hours of the seller handing it off to us.\n\nThanks for being awesome and using Circa, " \
                  "and feel free to reply with any feedback on how your experience with us was. We want to create " \
                  "the best way for students to buy and sell electronics." \
                  "\n\nSincerely,\n\nThe Circa Team"

WELCOME_NEW_USER = "Dear {},\n\nThank you for creating an account with us!  Circa offers the ability to buy and " \
                   "sell electronics locally.  We handle payment, shipping, returns, and fraud protection.\n\nThanks " \
                   "for being awesome and using Circa, and feel free to reply with any feedback on how your " \
                   "experience with us is. We want to create the best way for students to buy and sell electronics." \
                   "\n\nSincerely,\n\nThe Circa Team"


def offer_denied_notification(user, listing):
    content = OFFER_DENIED.format(
        user.username,
        listing.item.title,
        listing.current_offer,
        listing.buy_now_price,
        ALLOWED_HOSTS[0] + '/listing/{}'.format(listing.id)
    )

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="You no longer have the highest offer on {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def lost_listing_notification(user, listing):
    content = LOST_LISTING.format(user.username, listing.item.title)

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="Offers are no longer accepted on {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def listing_buy_now_notification(email, listing):
    content = LISTING_BUY_NOW.format(listing.item.title, listing.current_offer)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="You've bought {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def offer_accepted_notification(user, listing):
    content = OFFER_ACCEPTED.format(user.username, listing.item.title)

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="Offer accepted for {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()

    return message.mandrill_response[0]

def item_sold_notification(listing):
    price = listing.current_offer
    if price <= 30:
        earnings = 30
    else:
        earnings = price * Decimal(.90)

    content = ITEM_SOLD.format(listing.item.seller.username, listing.item.title, earnings)

    recipient = list()
    recipient.append(listing.item.seller.email)

    message = EmailMessage(
        subject="{} has sold".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()

    return message.mandrill_response[0]

def welcome_new_user_notification(user):
    content = WELCOME_NEW_USER.format(user.username)

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="Welcome to Circa!",
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

