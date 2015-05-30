from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from core.email import *
from core.models import Item, Listing, UserProfile
from core.forms import ItemForm, ListingForm, OfferForm
from core.keys import *
from django.contrib.auth.models import User
from django import forms
from decimal import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import json
import stripe
import requests

import datetime

# home page that shows items with associated listings that haven't already ended
def index(request):
    now = datetime.datetime.now()
    item_list = Item.objects.exclude(listing__isnull=True).exclude(listing__end_date__lte=now)\
        .order_by('listing__end_date')
    context = {'items': item_list}
    return render(request, 'index.html', context)

# posting an item
@login_required
def sell(request):

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return HttpResponseRedirect('/createlisting/'+str(item.id))

            # if form has errors?
    else:
        form = ItemForm()
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
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.current_offer = listing.starting_offer
            listing.save()
            item.listing = listing
            item.save()
            return HttpResponseRedirect('/listing/'+str(listing.id))

    else:
        form = ListingForm()

    context = {'item': item, 'form': form}
    return render(request, 'create_listing.html', context)

# Displays the requested listing along with info about listing item, or 404 page
# TODO use keys.py file to send public key to template
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    default_offer = listing.current_offer + Decimal(1.00)
    form = OfferForm(initial={'offer': default_offer})  # pre-populate offer with $1.00 above current offer

    if request.method == 'POST':
        token = request.POST.get('stripeToken', False)
        if token:  # Buy Now
            stripe.api_key = secret_key()
            email = request.POST['stripeEmail']
            amount_in_cents = int(listing.buy_now_price * 100)
            try:
                charge = stripe.Charge.create(
                    amount=amount_in_cents,
                    currency="usd",
                    source=token,
                    description="Circa Buy Now " + str(listing_id) + ": " + str(listing.item.title)
                )
                listing.buy_now_email = email
                listing.end_date = datetime.datetime.now()
                listing.current_offer = listing.buy_now_price
                listing.paid_for = True
                prev_offer_user = listing.current_offer_user
                if request.user.id:  # logged in user used buy it now
                    listing.current_offer_user= request.user
                    # TODO update item.buyer
                else:
                    listing.current_offer_user= None  # change when we create accounts for buy-now people
                listing.save()

                print(listing_buy_now_notification(email, listing))

                if prev_offer_user is not None:
                    print(lost_listing_notification(prev_offer_user, listing))

                return HttpResponseRedirect('/success/')
            except stripe.CardError:
                # context = {'error_message': "Your credit card was declined."}
                # return HttpResponseRedirect('/listing/'+str(listing.id))
                return HttpResponseRedirect('/')

        else:  # Make an Offer
            # TODO update item.buyer
            form = OfferForm(request.POST, listing=listing_id)
            if request.user.is_authenticated():
                if form.is_valid():
                    bid = form.cleaned_data['bid']
                    listing.current_offer = bid
                    listing.end_date = datetime.datetime.now() + datetime.timedelta(hours=1)
                    prev_offer_user = listing.current_offer_user
                    listing.current_offer_user= request.user

                    if prev_offer_user is not None:
                        offer_denied_notification(prev_offer_user, listing)

                    if bid * Decimal(1.0999) > listing.buy_now_price:
                        listing.buy_now_price = bid * Decimal(1.1000000)
                    listing.save()
                    return HttpResponseRedirect(request.path)
            else:  # unauthenticated user. Redirect to login page, then bring 'em back here.
                # TODO Figure out how to set next variable in context so manual url isn't needed
                # TODO If they sign up through this chain of events, bring them back here
                # TODO Save the bid they entered and prepopulate form with it when they are brought back here
                return HttpResponseRedirect('/accounts/login/?next=/listing/'+str(listing.id))

    item = listing.item
    minutes = 0
    seconds = 0
    if listing.end_date is None:
        status = 2
        # form.fields['bid'].widget = forms.HiddenInput()
    elif listing.end_date < datetime.datetime.now():
        status = 1
    else:
        status = 0
        minutes, seconds = divmod((listing.end_date - datetime.datetime.now()).total_seconds(), 60)
        minutes = round(minutes)
        seconds = round(seconds)
    amount = int(listing.buy_now_price * 100)
    stripe_amount = json.dumps(amount)
    item_json = json.dumps(item.title)
    context = {'listing': listing, 'form': form,'item': item, 'amount': stripe_amount, 'status': status,
               'minutes': minutes, 'seconds': seconds, 'stripe_key': public_key()}
    return render(request, 'listing_detail.html', context)

# Shows all outstanding, unpaid listings for user
@login_required
def pending(request):
    # find lisings where user is the highest bidder, payment has not been received, and have already ended
    now = datetime.datetime.now()
    user = request.user
    items = []
    listings = Listing.objects.filter(current_bidder=user).filter(paid_for=False).filter(end_date__lt=now)
    for listing in listings:
        items.append(listing.item)
    return render(request, 'pending.html', {'items': items})

# uses stripe checkout for user to pay for listing once offer has been accepted
@login_required
def pay(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    item = listing.item
    if request.user.id is not listing.current_offer_user.id:  # user is trying to pay for someone else's listing
        raise PermissionDenied
    if listing.paid_for:  # user already paid for item
        return render(request, 'expired.html')
    if request.method == 'POST':
        token = request.POST.get('stripeToken', False)
        email = request.POST['stripeEmail']
        if token:  # Successfully submitted Stripe
            stripe.api_key = secret_key()
            # email = request.POST['stripeEmail']
            amount_in_cents = int(listing.current_offer * 100)
            try:
                charge = stripe.Charge.create(
                    amount=amount_in_cents,
                    currency="usd",
                    source=token,
                    description="Circa Sale " + str(listing_id) + ": " + str(listing.item.title)
                )
                item.buyer = request.user
                listing.paid_for = True
                listing.save()
                item.save()

                listing_buy_now_notification(email, listing)

                return HttpResponseRedirect('/pending/')

            except stripe.CardError:
                raise Exception
                # context = {'error_message':"Your credit card was declined."}
                # return HttpResponseRedirect(request.path)
        else:
            return HttpResponseRedirect('/todo/')
    elapsed = datetime.datetime.now() - listing.end_date
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    amount = int(listing.current_offer * 100)
    stripe_amount = json.dumps(amount)
    context = {'days': days, 'hours': hours, 'minutes': minutes,
               'listing': listing, 'amount': stripe_amount, 'item': item}
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
        profile = UserProfile(user = current_user)
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
    return render(request, 'about.html')

def success(request):
    return render(request, 'success.html')

def help(request):
    return render(request, 'help.html')

# remove from production
def todo(request):
    return render(request,'todo.html')