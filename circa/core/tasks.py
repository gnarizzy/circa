from background_task import background
from core.models import User, Listing
from core.email import offer_accepted_notification
from circa.settings import COMMISSION_FLAT, COMMISSION_PERCENT, COMMISSION_BREAKEVEN
from decimal import *
from django.core.mail import EmailMessage

import datetime

OFFER_OVER = "Dear {},\n\nYour item, {}, has a winning offer!  Your total earnings are predicted to be ${}, which " \
             "will be given to you upon pick up of the item.  Please reply to this email with your address and " \
             "preferred pick-up time.\n\nThank you for using Circa!  If you have any feedback on your " \
             "experience, please reply to this email and let us know.  We want to be the best way for students to buy " \
             "and sell electronics locally." \
             "\n\nSincerely\n\nThe Circa Team"

@background(schedule=datetime.timedelta(hours=1))
def queue_for_email_notifications(user_id, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if user_id is not None and user_id is listing.current_offer_user.id:
        buyer = User.objects.get(pk=user_id)
        offer_accepted_notification(buyer, listing)

        offer_accepted_seller_notification(listing)
    return

def offer_accepted_seller_notification(listing):
    price = listing.current_offer
    if price <= COMMISSION_BREAKEVEN:
        earnings = price - Decimal(COMMISSION_FLAT)
    else:
        earnings = price * Decimal(1 - COMMISSION_PERCENT)

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