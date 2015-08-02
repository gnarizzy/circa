# A helper module to generate emails and avoid spaghetti code
from circa.settings import ALLOWED_HOSTS
from django.core.mail import EmailMessage
from core.payout import calc_payout


LISTING_BOUGHT_SELLER =    \
    "Dear {},\n\nYour item, {}, has been sold!  Your total earnings are  ${}, which " \
    "will be given to you within 24 hours of pick up.  Please reply to this email with your address and " \
    "preferred pick-up time.\n\nThank you for using Circa!  If you have any feedback on your " \
    "experience, please reply to this email and let us know.  We want to be the best way " \
    "to buy and sell locally." \
    "\n\nSincerely\n\nThe Circa Team"

LISTING_BOUGHT_BUYER = \
    "Hello,\n\nCongratulations on getting {}! This email is to confirm that you paid ${} for this " \
    "item. We also want to verify that it will be shipped to the following address:\n\n" \
    "{}\n\n" \
    "If this is not correct, respond to this email ASAP with your preferred delivery address. " \
    "Your item will be delivered within 24 hours of the seller handing it off to us.\n\n" \
    "Thanks " \
    "for being awesome and using Circa, and feel free to reply with any feedback on how your " \
    "experience " \
    "with us was. We want to create the best way to buy and sell locally." \
    "\n\nSincerely,\n\nThe Circa Team"

LISTING_FREE_CONFIRMATION = \
    "Hello,\n\nCongratulations on getting {}! This email is to confirm that you ordered " \
    "this item for FREE! Your item will be delivered within 24 hours of the seller handing it off to " \
    "us.\n\nThanks for being awesome and using Circa, and feel free to reply with any feedback on how " \
    "your experience " \
    "with us was. We want to create the best way to buy and sell locally." \
    "\n\nSincerely,\n\nThe Circa Team"

ADMIN_NOTIFICATION = \
    "Item: {}\n" + \
    "Seller: {}\n" + \
    "Buyer: {}\n" + \
    "Buyer Address: {}"

WELCOME_NEW_USER = \
    "Hey {},\n\nThanks for signing up for Circa! We're working to build the easiest way to buy and " \
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
    "\n\nSincerely,\n\nAndrew\n\nCo-Founder of Circa and Head Delivery Boy"


def listing_bought_buyer_notification(listing):
    addr = listing.item.buyer.userprofile.address

    addr_str = addr.address_line_1

    if addr.address_line_2 is not None:
        addr_str += "\n" + addr.address_line_2

    addr_str += "\n" + addr.city + ", " + addr.state + " " + addr.zipcode

    if addr.special_instructions is not None:
        addr_str += "\nSpecial Instructions: " + addr.special_instructions

    content = LISTING_BOUGHT_BUYER.format(listing.item.title, listing.price, addr_str)

    recipient = list()
    recipient.append(listing.item.buyer.email)

    message = EmailMessage(
        subject="You've bought {}".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()


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


def listing_bought_seller_notification(listing):
    price = calc_payout(listing.price)
    earnings = round(price, 2)

    content = LISTING_BOUGHT_SELLER.format(listing.item.seller.username, listing.item.title, earnings)

    recipient = list()
    recipient.append(listing.item.seller.email)

    message = EmailMessage(
        subject="{} has sold!".format(listing.item.title),
        body=content,
        to=recipient
    )
    message.send()


def admin_notification_of_sale(listing):
    addr = listing.item.buyer.userprofile.address

    addr_str = addr.address_line_1

    if addr.address_line_2 is not '':
        addr_str += "\n" + addr.address_line_2

    addr_str += "\n" + addr.city + ", " + addr.state + " " + addr.zipcode

    if addr.special_instructions is not '':
        addr_str += "\n\nSpecial Instructions: " + addr.special_instructions

    content = ADMIN_NOTIFICATION.format(
        listing.item.title,
        listing.item.seller.username,
        listing.item.buyer.username,
        addr_str
    )

    recipient = list()
    recipient.append("support@usecirca.com")

    message = EmailMessage(
        subject="Pending Delivery",
        body=content,
        to=recipient
    )
    message.send()


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
