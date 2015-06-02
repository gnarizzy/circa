from background_task import background
from core.models import User, Listing
from core.email import offer_accepted_notification, offer_accepted_seller_notification

import datetime


@background(schedule=datetime.timedelta(hours=1))
def queue_for_email_notifications(user_id, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if user_id is not None and user_id is listing.current_offer_user.id:
        buyer = User.objects.get(pk=user_id)
        offer_accepted_notification(buyer, listing)

        offer_accepted_seller_notification(listing)
    return
