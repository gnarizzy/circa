# A helper module to generate emails and avoid spaghetti code
from django.core.mail import EmailMessage
from circa.settings import ALLOWED_HOSTS

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

### THIS NEEDS TO BE RE-WORKED
OFFER_ACCEPTED = "Dear {},\n\nYour offer on {} has been accepted! Can you reply to this email with your address " \
                 "and preferred delivery time? Your item will be delivered within 24 hours of the seller handing it off " \
                 "to us.\n\nThanks for being awesome and using Circa, and feel free to reply with any feedback on how " \
                 "your experience with us was. We want to create the best way for students to buy and sell " \
                 "electronics." \
                 "\n\nSincerely,\n\nThe Circa Team"
### READ ABOVE

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
        ALLOWED_HOSTS[0] + '/auction/{}'.format(listing.id)
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

def auction_won_buy_now_notification(email, auction):
    content = LISTING_BUY_NOW.format(auction.item.title, auction.current_bid)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="You've bought {}".format(auction.item.title),
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

