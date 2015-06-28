# A helper module to generate emails and avoid spaghetti code
from circa.settings import ALLOWED_HOSTS
from django.core.mail import EmailMessage
from core.models import User, Listing
from core.payout import calc_payout
from decimal import *


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

OFFER_ACCEPTED = "Dear {},\n\nYour offer on {} has been accepted!\n\nPlease navigate to " \
                 "http://www.usecirca.com/pending/ to pay for your item.\n\nCan you reply with your address (no PO " \
                 "boxes--we can't deliver to those!) and any special delivery instructions?  Once paid for, the item " \
                 "will be delivered " \
                 "within 24 hours of the seller handing it off to us.\n\nThanks for being awesome and using Circa!  " \
                 "Feel free to reply with any feedback on how your experience was.  We want to create the best way " \
                 "to buy and sell locally." \
                 "\n\nSincerely,\n\nThe Circa Team"

LISTING_BOUGHT = "Dear {},\n\nYour item, {}, has been sold!  Your total earnings are  ${}, which " \
                 "will be given to you upon pick up of the item.  Please reply to this email with your address and " \
                 "preferred pick-up time.\n\nThank you for using Circa!  If you have any feedback on your " \
                 "experience, please reply to this email and let us know.  We want to be the best way " \
                 "to buy and sell locally." \
                 "\n\nSincerely\n\nThe Circa Team"

OFFER_OVER = "Dear {},\n\nYour item, {}, has a winning offer!  Your total earnings are predicted to be ${}, which " \
             "will be given to you upon pick up of the item.  Please reply to this email with your address and " \
             "preferred pick-up time.\n\nThank you for using Circa!  If you have any feedback on your " \
             "experience, please reply to this email and let us know.  We want to be the best way to buy " \
             "and sell locally." \
             "\n\nSincerely\n\nThe Circa Team"

LISTING_BUY_NOW = "Hello,\n\nCongratulations on getting {}! This email is to confirm that you paid ${} for this " \
                  "item.  Can you reply with your address (no PO boxes--we can't deliver to those!) and any special " \
                  "delivery " \
                  "instructions? Your item will be delivered within 24 hours of the seller handing it off to us.\n\n" \
                  "Thanks " \
                  "for being awesome and using Circa, and feel free to reply with any feedback on how your " \
                  "experience " \
                  "with us was. We want to create the best way to buy and sell locally." \
                  "\n\nSincerely,\n\nThe Circa Team"

LISTING_PAID_FOR = "Hello,\n\nCongratulations on getting {}! This email is to confirm that you paid ${} for this " \
                   "item.  If you haven't already, please give us an address to deliver to (no PO boxes--we can't " \
                   "deliver to those!).  Your item will be delivered within 24 hours of the seller handing it " \
                   "off to us.\n\nThanks " \
                   "for being awesome and using Circa, and feel free to reply with any feedback on how your " \
                   "experience " \
                   "with us was. We want to create the best way to buy and sell locally." \
                   "\n\nSincerely,\n\nThe Circa Team"

LISTING_FREE_CONFIRMATION = "Hello,\n\nCongratulations on getting {}! This email is to confirm that you ordered " \
                  "this item for FREE! Your item will be delivered within 24 hours of the seller handing it off to " \
                  "us.\n\nThanks for being awesome and using Circa, and feel free to reply with any feedback on how " \
                  "your experience " \
                  "with us was. We want to create the best way to buy and sell locally." \
                  "\n\nSincerely,\n\nThe Circa Team"

WELCOME_NEW_USER = "Hey {},\n\nThanks for signing up for Circa! We're working to build the easiest way to buy and " \
                   "sell locally, where haggling, meet-ups, and scams are a thing of the " \
                   "past.\n\nHere's how it works:\n\n1) Sellers post stuff they want to sell\n\n2) Buyers " \
                   "make an offer. If nobody beats that offer within an hour, the offer " \
                   "is accepted and the buyer pays securely online. If you buy now, you instantly win the " \
                   "item.\n\n3) We pick up the item from the seller, " \
                   "deliver it to the buyer, and the seller gets paid!\n\nAnything you buy on Circa is protected by " \
                   "our no-questions-asked 30 day refund policy. And if you have anything you'd like to sell, " \
                   "visit http://www.usecirca.com/sell and start listing your stuff! One of our sellers made nearly " \
                   "$200 in 24 hours selling on Circa!\n\nThanks again for signing up, and if you have any " \
                   "questions, feel free to check out http://www.usecirca.com/about/ or reply to this email. You " \
                   "can also follow us on Facebook (https://www.facebook.com/usecirca) or visit " \
                   "http://usecirca.com to stay updated with the latest deals." \
                   "\n\nSincerely,\n\nAndrew\n\nCS '15"

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

def listing_bought_notification(email, listing):
    content = LISTING_PAID_FOR.format(listing.item.title, listing.current_offer)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="You've bought {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def listing_bought_discount_notification(email, listing_title, listing_discounted_price):
    content = LISTING_PAID_FOR.format(listing_title, listing_discounted_price)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="You've bought {}".format(listing_title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def listing_free_confirm_notification(email, listing):
    content = LISTING_FREE_CONFIRMATION.format(listing.item.title)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="You've ordered {}".format(listing.item.title),
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

def listing_bought_seller_notification(listing):
    price = calc_payout(listing.current_offer)
    earnings = round(price, 2)

    content = LISTING_BOUGHT.format(listing.item.seller.username, listing.item.title, earnings)

    recipient = list()
    recipient.append(listing.item.seller.email)

    message = EmailMessage(
        subject="{} has sold!".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()

    return message.mandrill_response[0]

def offer_accepted_seller_notification(listing):
    price = calc_payout(listing.current_offer)
    earnings = round(price, 2)

    content = OFFER_OVER.format(listing.item.seller.username, listing.item.title, earnings)

    recipient = list()
    recipient.append(listing.item.seller.email)

    message = EmailMessage(
        subject="{} has a winning offer!".format(listing.item.title),
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
        to=recipient,
        from_email="andrew@usecirca.com"
    )
    message.send()

    return message.mandrill_response[0]

def welcome_new_user_fb_notification(username, email):
    content = WELCOME_NEW_USER.format(username)

    recipient = list()
    recipient.append(email)

    message = EmailMessage(
        subject="Welcome to Circa!",
        body=content,
        to=recipient,
        from_email="andrew@usecirca.com"
    )
    message.send()

    return message.mandrill_response[0]

