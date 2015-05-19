# A helper module to generate emails and avoid spaghetti code
from django.core.mail import EmailMessage
from circa.settings import ALLOWED_HOSTS

import datetime


OUT_BID = "Hey {},\n\nUnfortunately, you've been outbid on {}. The current bid is ${}, and the auction will end " \
          "in about {}. If you don't want to this to happen again, you can buy the item now for ${}.\n\nThe "\
          "auction can be found here: {}\n\n" \
          "Thanks for using Circa, and feel free to reply to this email with any questions or feedback." \
          "\n\nSincerely,\n\nThe Circa Team"

LOST_AUCTION = "Hey {},\n\nUnfortunately, someone has used the buy now option on {}, which " \
               "has ended the auction. To avoid this in future auctions, you can click \"Buy Now\" to pay for the " \
               "item immediately and guarantee that you'll get it within 24 hours.\n\nThanks for using Circa, and " \
               "feel free to reply to this email with any questions or feedback.\n\nSincerely,\n\nThe Circa Team"

AUCTION_WON = "Dear {},\n\nCongratulations on winning {}! Can you reply to this email with your address " \
              "and preferred delivery time? Your item will be delivered within 24 hours of the seller handing it off " \
              "to us.\nThanks for being awesome and using Circa, and feel free to reply with any feedback on how " \
              "your experience with us was. We want to create the best way for students to buy and sell " \
              "electronics.\n\n" \
              "Sincerely,\n\nThe Circa Team"

WELCOME_NEW_USER = "Dear {},\n\nThank you for creating an account with us!  Circa offers the ability to buy and " \
                   "sell lightly used electronics locally.  We handle payment, shipping, returns, and fraud " \
                   "protection.\n\nThanks for being awesome and using Circa, and feel free to reply with any feedback " \
                   "on how your experience with us is. We want to create the best way for students to buy and sell " \
                   "electronics.\n\n" \
                   "Sincerely,\n\nThe Circa Team"


def out_bid_notification(user, auction):
    time_left = auction.end_date - datetime.datetime.now()
    hours = time_left.total_seconds() / 3600
    minutes = (time_left.total_seconds() / 60) % 60
    if hours < 1:
        time_string = '%d minutes' % minutes
    else:
        time_string = '%d hours and %d minutes' % (hours, minutes)

    content = OUT_BID.format(
        user.username,
        auction.item.title,
        auction.current_bid,
        time_string,
        auction.buy_now_price,
        ALLOWED_HOSTS[0] + '/auction/{}'.format(auction.id)
    )

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="You've been outbid on {}".format(auction.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def lost_auction_notification(user, auction):
    content = LOST_AUCTION.format(user.username, auction.item.title)

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="You've lost the auction for {}".format(auction.item.title),
        body=content,
        to=recipient
    )
    message.send()
    return message.mandrill_response[0]

def auction_won_notification(user, auction):
    content = AUCTION_WON.format(user.username, auction.item.title)

    recipient = list()
    recipient.append(user.email)

    message = EmailMessage(
        subject="You've won {}".format(auction.item.title),
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

