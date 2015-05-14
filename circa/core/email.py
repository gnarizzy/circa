# A helper module to generate emails and avoid spaghetti code
from django.core.mail import EmailMessage

import datetime


OUT_BID = "Hey {},\nUnfortunately, you've been outbid on {}. The current bid is ${}, and the auction will end " \
          "in about {} hours. If you don't want to this to happen again, you can buy the item now for ${}.\n\n" \
          "Thanks for using Circa, and feel free to reach out at support@usecirca.com with any questions or feedback." \
          "\n\nSincerely,\bThe Circa Team"

AUCTION_WON = "Dear {},\n\nCongratulations on winning {}! Can you reply to this email with your address " \
              "and preferred delivery time? Your item will be delivered within 24 hours of the seller handing it off " \
              "to us.\nThanks for being awesome and using Circa, and feel free to reply with any feedback on how " \
              "your experience with us was. We want to create the best way for students to buy and sell " \
              "electronics.\n\n" \
              "Sincerely,\nAndrew\nCS '15 and Co-Founder of Circa"

WELCOME_NEW_USER = "Dear {},\n\nThank you for creating an account with us!  Circa offers the ability to buy and " \
                   "sell lightly used electronics locally.  We handled payment, shipping, returns, and fraud " \
                   "protection.\n\nThanks for being awesome and using Circa, and feel free to reply with any feedback " \
                   "on how your experience with us is. We want to create the best way for students to buy and sell " \
                   "electronics.\n\n" \
                   "Sincerely,\nAndrew\nCS '15 and Co-Founder of Circa"


def out_bid_notification(user, auction):
    hours_left = datetime.datetime.now() - auction.end_date
    hours_left = hours_left.seconds / 3600
    content = OUT_BID.format(user.username, auction.item.title, auction.current_bid, hours_left, auction.buy_now_price)

    message = EmailMessage(
        subject="You've been Out Bid on {}".format(auction.item.title),
        body=content,
        to=user.email
    )
    message.send()
    return message.mandrill_response[0]


def auction_won_notification(user, auction):
    content = AUCTION_WON.format(user.username, auction.item.title)

    message = EmailMessage(
        subject="You've won {}".format(auction.item.title),
        body=content,
        to=user.email
    )
    message.send()
    return message.mandrill_response[0]


def welcome_new_user_notification(user):
    content = WELCOME_NEW_USER.format(user.username)

    message = EmailMessage(
        subject="Welcome to Circa!",
        body=content,
        to=user.email
    )
    message.send()
    return message.mandrill_response[0]

