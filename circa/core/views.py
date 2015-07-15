from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from core.email import listing_bought_notification, listing_bought_seller_notification, lost_listing_notification, \
    offer_denied_notification, listing_free_confirm_notification, listing_bought_discount_notification
from core.models import Item, Listing, UserProfile, PromoCode
from core.forms import ItemForm, ListingForm, EditListingForm, OfferForm, PromoForm, AddressForm
from core.keys import *
from core.payout import calc_payout
from core.zipcode import zipcodes
from django.contrib.auth.models import User
from django import forms
from decimal import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from core.tasks import queue_for_email_notifications
import json
import stripe
import requests

import datetime

# Home page that shows items with associated listings that haven't already ended
def index(request):
    now = datetime.datetime.now()
    item_list = Item.objects.exclude(listing__isnull=True).exclude(listing__end_date__lte=now) \
        .order_by('-pk')
    context = {'items': item_list}
    return render(request, 'index.html', context)

# Displays home page, but with specific category items only
def category(request, category_name):
    if category_name in Item.CATEGORY_NAMES.keys():
        now = datetime.datetime.now()
        item_list = Item.objects.exclude(listing__isnull=True).exclude(listing__end_date__lte=now) \
            .filter(category=Item.CATEGORY_NAMES[category_name]).order_by('-pk')
        context = {'items': item_list, 'category': Item.CATEGORY_NAMES[category_name]}
        return render(request, 'index.html', context)
    else:
        return HttpResponseRedirect('/')

# Posting an item
@login_required
def sell(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, seller=request.user)

        if form.is_valid():
            item = form.save()
            return HttpResponseRedirect('/createlisting/' + str(item.id))
    else:
        form = ItemForm(seller=request.user)
    return render(request, 'sell.html', {'form': form})

# creating an listing for previously posted item
@login_required
def create_listing(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if item.listing:  # item already has a listing
        return render(request, 'expired.html')

    if item.seller.id is not request.user.id:  # some bro wants to create a listing for an item that is not his!
        raise PermissionDenied

    if request.method == 'POST':
        form = ListingForm(request.POST, item=item)

        if form.is_valid():
            listing = form.save()
            return HttpResponseRedirect('/listing/' + str(listing.id))

    else:
        form = ListingForm(item=item)

    context = {'item': item, 'form': form}
    return render(request, 'create_listing.html', context)

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    item = listing.item

    # Listing already ended
    if listing.end_date and listing.end_date < datetime.datetime.now():
        return render(request, 'expired.html')

    # Listing is already paid for... shouldn't ever get here since end date should've passed, but just in case
    if listing.paid_for:
        return render(request, 'expired.html')

    # Some bro wants to edit a listing that is not his!
    if item.seller.id is not request.user.id:
        raise PermissionDenied

    if request.method == 'POST':
        form = EditListingForm(request.POST, listing=listing)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/listing/' + str(listing.id))

    else:
        form = EditListingForm(
            initial={
                'title': item.title,
                'description': item.description,
                'category': item.category,
                'starting_offer': listing.starting_offer,
                'buy_now_price': listing.buy_now_price,
                'zipcode': listing.zipcode
            }, listing=listing)

    context = {'item': item, 'listing': listing, 'form': form}
    return render(request, 'edit_listing.html', context)


# Displays the requested listing along with info about listing item, or 404 page
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    default_offer = listing.current_offer + Decimal(1.00) if listing.current_offer else listing.starting_offer
    # Pre-populate offer with $1.00 above current offer or starting offer
    form = OfferForm(initial={'offer': default_offer}, listing=listing, user=request.user)

    if request.method == 'POST':
        token = request.POST.get('stripeToken', False)

        # Buy Now
        if token:
            stripe.api_key = secret_key()
            email = request.POST['stripeEmail']
            amount_in_cents = int(listing.buy_now_price * 100)
            try:
                prev_offer_user = listing.current_offer_user
                charge = stripe.Charge.create(
                    amount=amount_in_cents,
                    currency="usd",
                    source=token,
                    description="Circa Buy Now " + str(listing_id) + ": " + str(listing.item.title)
                )
                update_listing(listing, request, email)

                listing_bought_notification(email, listing)
                listing_bought_seller_notification(listing)

                if prev_offer_user is not None and prev_offer_user.email is not email:
                    lost_listing_notification(prev_offer_user, listing)

                return HttpResponseRedirect('/success/')
            except stripe.error.CardError:
                messages.error(request, 'Your credit card was declined.  If you\'re sure that your card is valid, '
                                        'the problem may be with our payment processing system.  Wait an hour or '
                                        'so and try again.  If the problem persists, please contact us at '
                                        'support@usecirca.com so we can help sort out the issue.')
                return HttpResponseRedirect(request.path)

        # Make an Offer
        else:
            # TODO update item.buyer
            form = OfferForm(request.POST, listing=listing, user=request.user)
            if request.user.is_authenticated():

                if form.is_valid():
                    prev_offer_user = listing.current_offer_user
                    form.save()

                    if prev_offer_user is not None and prev_offer_user is not request.user:
                        offer_denied_notification(prev_offer_user, listing)

                    queue_for_email_notifications(request.user.id, listing.id)

                    return HttpResponseRedirect(request.path)

            # Unauthenticated user. Redirect to login page, then bring 'em back here.
            else:
                # TODO Figure out how to set next variable in context so manual url isn't needed
                # TODO If they sign up through this chain of events, bring them back here
                # TODO Save the offer they entered and pre-populate form with it when they are brought back here
                return HttpResponseRedirect('/accounts/login/?next=/listing/' + str(listing.id))

    item = listing.item
    status, minutes, seconds = get_status(listing)
    amount = int(listing.buy_now_price * 100)
    stripe_amount = json.dumps(amount)
    item_json = json.dumps(item.title)
    context = {'listing': listing, 'form': form, 'item': item, 'amount': stripe_amount, 'status': status,
               'minutes': minutes, 'seconds': seconds, 'stripe_key': public_key()}
    return render(request, 'listing_detail.html', context)

# Helper method for listing_detail
def update_listing(listing, request, email):
    listing.buy_now_email = email
    listing.end_date = datetime.datetime.now()
    listing.current_offer = listing.buy_now_price
    listing.paid_for = True
    listing.payout = calc_payout(listing.buy_now_price)
    if request.user.id:  # logged in user used buy it now
        listing.current_offer_user = request.user
        listing.item.buyer = request.user
    else:
        listing.current_offer_user = None  # change when we create accounts for buy-now people
    listing.save()

# Helper method for listing_detail
def get_status(listing):
    minutes = 0
    seconds = 0
    if listing.end_date is None:
        status = 2
    elif listing.end_date < datetime.datetime.now():
        status = 1
    else:
        status = 0
        minutes, seconds = divmod((listing.end_date - datetime.datetime.now()).total_seconds(), 60)
        minutes = round(minutes)
        seconds = round(seconds)

    return status, minutes, seconds

# Shows all outstanding, unpaid listings for user
@login_required
def pending(request):
    if not request.user.userprofile.address:
        return HttpResponseRedirect('/address/?next=/pending/')

    # find listings where user is the highest offer user, payment has not been received, and have already ended
    now = datetime.datetime.now()
    user = request.user
    items = []
    listings = Listing.objects.filter(current_offer_user=user).filter(paid_for=False).filter(end_date__lt=now)
    for listing in listings:
        try:
            items.append(listing.item)
        except ObjectDoesNotExist:  # listing has no related item
            pass
    return render(request, 'pending.html', {'items': items})


# Uses stripe checkout for user to pay for listing once offer has been accepted
@login_required
def pay(request, listing_id):
    free = 0
    listing = get_object_or_404(Listing, pk=listing_id)
    item = listing.item
    user_address = request.user.userprofile.address

    # User is trying to pay for someone else's listing
    if request.user.id is not listing.current_offer_user.id:
        raise PermissionDenied

    # User already paid for item
    if listing.paid_for:
        return render(request, 'expired.html')

    # Amount after discount is under 31 cents, meaning we'd barely make anything or even lose money
    if listing.current_offer - listing.discount < Decimal(0.50):
        free = 1

    if request.method == 'POST':
        form = PromoForm(request.POST, user=request.user, listing=listing)
        token = request.POST.get('stripeToken', False)
        # Successfully submitted Stripe
        if token:
            email = request.POST['stripeEmail']
            stripe.api_key = secret_key()
            amount_in_cents = int((listing.current_offer - listing.discount) * 100)
            try:
                charge = stripe.Charge.create(
                    amount=amount_in_cents,
                    currency="usd",
                    source=token,
                    description="Circa Sale " + str(listing_id) + ": " + str(listing.item.title)
                )
                item.buyer = request.user
                listing.paid_for = True
                listing.payout = calc_payout(listing.current_offer)
                listing.save()
                item.save()

                if listing.discount > Decimal(0.00):
                    listing_bought_discount_notification(email, listing.item.title,
                                                         listing.current_offer - listing.discount)
                else:
                    listing_bought_notification(email, listing)

                return HttpResponseRedirect('/success/')

            except stripe.error.CardError as e:
                messages.error(request, 'Your credit card was declined.  If you\'re sure that your card is valid, '
                                        'the problem may be with our payment processing system.  Wait an hour or '
                                        'so and try again.  If the problem persists, please contact us at '
                                        'support@usecirca.com so we can help sort out the issue.')
                return HttpResponseRedirect(request.path)

        else:
            # Submit promo code form
            if 'confirm_' in request.POST:  # confirm button
                listing.paid_for = True
                listing.payout = calc_payout(listing.current_offer)
                listing.save()
                item.save()

                listing_free_confirm_notification(listing.current_offer_user.email, listing)

                return HttpResponseRedirect('/success/')

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(request.path)

    else:
        form = PromoForm(user=request.user, listing=listing)

    elapsed = datetime.datetime.now() - listing.end_date
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if listing.discount > 0:
        amount = int((listing.current_offer - listing.discount) * 100)
        discounted_price = listing.current_offer - listing.discount

    else:
        amount = int(listing.current_offer * 100)
        discounted_price = None

    stripe_amount = json.dumps(amount)
    context = {'days': days, 'hours': hours, 'minutes': minutes, 'stripe_key': public_key(),
               'listing': listing, 'amount': stripe_amount, 'discounted_price': discounted_price, 'item': item,
               'form': form, 'free': free, 'address': user_address}
    return render(request, 'pay.html', context)


# Allows users to connect their Stripe accounts to Circa
# To prevent CSRF, add state token and validate for that
@login_required
def connect(request):
    is_connected = False
    current_user = request.user
    if hasattr(current_user, 'UserProfile'):
        if UserProfile.alt_id:  # already connected to Stripe
            is_connected = True
    else:
        is_connected = False
    if not is_connected:
        profile = UserProfile(user=current_user)
        stripe.api_key = secret_key()
        account = stripe.Account.create(country='US', managed=True)
        profile.alt_id = account['id']
        # profile.save()
        is_connected = True
    context = {'connected': is_connected}
    return render(request, 'connect.html', context)


def terms(request):
    return render(request, 'terms.html')


def about(request):
    context = {'zipcodes': zipcodes(), 'zip_len': len(zipcodes())}
    return render(request, 'about.html', context)


def success(request):
    return render(request, 'success.html')


def help(request):
    context = {'zipcodes': zipcodes(), 'zip_len': len(zipcodes())}
    return render(request, 'help.html', context)


@login_required
def dashboard(request):
    now = datetime.datetime.now()
    user = request.user
    pending_num = Listing.objects.filter(current_offer_user=user).filter(paid_for=False).filter(end_date__lt=now).count()
    offers_num = Listing.objects.filter(current_offer_user=user).filter(end_date__gt=now).count()
    earnings_num = 0
    active_items_num = 0
    items = Item.objects.filter(seller=user)
    for item in items:
        if item.listing:
            earnings_num += item.listing.payout

            # Offer on listing, but still time left
            if item.listing.end_date and item.listing.end_date > datetime.datetime.now():
                active_items_num += 1

            # Listing over but not paid for yet
            if item.listing.end_date and item.listing.end_date < now and not item.listing.paid_for:
                active_items_num += 1

            # Listed item, but no offers
            if not item.listing.end_date:
                active_items_num += 1
    orders = []
    bought = Listing.objects.filter(current_offer_user=user).filter(paid_for=True)
    for order in bought:
        orders.append(order.item)

    context = {'pending': pending_num, 'offers': offers_num, 'earnings': earnings_num,
               'orders': orders, 'active_items': active_items_num}
    return render(request, 'dashboard.html', context)


@login_required
def offers(request):  # not very DRY
    now = datetime.datetime.now()
    user = request.user
    listings_list = Listing.objects.filter(current_offer_user=user).filter(end_date__gt=now)
    context = {'listings': listings_list}
    return render(request, 'offers.html', context)


@login_required
def earnings(request):  # not very DRY
    total_earnings = 0
    user = request.user
    items = Item.objects.filter(seller=user)
    items_list = []
    for item in items:
        if item.listing and item.listing.payout > 0:
            items_list.append(item)
            total_earnings += item.listing.payout
    context = {'items': items_list, 'earnings': total_earnings}
    return render(request, 'earnings.html', context)


# Remove from production (teehee)
def todo(request):
    return render(request, 'todo.html')


# Active items for seller: items where offer is accepted but not sold, and items not yet sold
@login_required
def active_items(request):
    now = datetime.datetime.now()
    user = request.user
    items_list = Item.objects.filter(seller=user)
    active_items_list = []
    unpaid_items_list = []
    no_offers_items_list = []
    for item in items_list:
        if item.listing:
            if item.listing.end_date:
                # Active listing with offers
                if item.listing.end_date > now:
                    active_items_list.append(item)

                # Offer hasn't been paid for
                elif item.listing.end_date < now and not item.listing.paid_for:
                    unpaid_items_list.append(item)

            # listed item with no end date means no offers have been made
            else:
                no_offers_items_list.append(item)

    context = {'active_items': active_items_list, 'unpaid_items': unpaid_items_list, 'no_offers': no_offers_items_list}
    return render(request, 'active_items.html', context)

@login_required
def address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        form = AddressForm(initial={'state': AddressForm.INITIAL_STATE}, user=request.user)

    context = {'form': form, 'next': request.GET.get('next', '/')}
    return render(request, 'address.html', context)
