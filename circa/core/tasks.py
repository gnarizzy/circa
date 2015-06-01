from background_task import background
from core.models import User, Listing
from core.email import offer_accepted_notification, item_sold_notification

import datetime


@background(schedule=datetime.timedelta(hours=1))
def queue_for_email_notifications(user_id, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if user_id is listing.current_offer_user.id:
        # Email Buyer
        buyer = User.objects.get(pk=user_id)
        offer_accepted_notification(buyer, listing)

        # Email Seller
        item_sold_notification(listing)
    return
