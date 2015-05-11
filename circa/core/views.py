from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from core.models import Item, Auction
from core.forms import ItemForm, AuctionForm, BidForm
from core.keys import test_secret_key, secret_key
from django.contrib.auth.models import User
from django import forms
from decimal import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import json
import stripe


import datetime

#home page that shows items with associated auctions that haven't already ended
def index(request):
    now = datetime.datetime.now()
    item_list = Item.objects.exclude(auction__isnull=True).exclude(auction__end_date__lte = now)\
        .order_by('auction__end_date')
    context = {'items':item_list}
    return render(request, 'index.html', context)

#posting an item
@login_required
def sell(request):

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return HttpResponseRedirect('/createauction/'+str(item.id))

            #if form has errors?
    else:
        form = ItemForm()
    return render(request,'sell.html',{'form':form})

#creating an auction for previously posted item
@login_required
def create_auction(request, itemid):
    item = get_object_or_404(Item, pk=itemid)

    if item.auction: #item already has an auction...
        #return expired page
        return render(request,'expired.html')

    if item.seller.id is not request.user.id: #some bro wants to create an auction for an item that is not his!
        raise PermissionDenied

    if request.method == 'POST':
        form = AuctionForm(request.POST)

        if form.is_valid():
            auction = form.save(commit=False)
            auction.current_bid = auction.starting_bid
            now = datetime.datetime.now()
            duration = datetime.timedelta(days=auction.duration)
            end_date = now + duration
            auction.end_date = end_date
            auction.save()
            item.auction = auction
            item.save()
            return HttpResponseRedirect('/auction/'+str(auction.id))

    else:
        form = AuctionForm()

    context = {'item':item,'form':form}
    return render(request, 'create_auction.html', context)

#Displays the requested auction along with info about auction item, or 404 page
#TODO use keys.py file to send public key to template
def auction_detail(request, auctionid):
    auction = get_object_or_404(Auction, pk=auctionid)

    if request.method == 'POST':
          token = request.POST.get('stripeToken', False)
          if token: #Buy Now
            stripe.api_key = test_secret_key()
            email = request.POST['stripeEmail']
            amount_in_cents = int(auction.buy_now_price * 100)
            try:
                charge = stripe.Charge.create(
                    amount = amount_in_cents,
                    currency = "usd",
                    source = token,
                    description = "Circa Buy Now "+ str(auctionid) + ": " + str(auction.item.title)
                )
                auction.buy_now_email = email
                auction.end_date = datetime.datetime.now()
                auction.current_bid = auction.buy_now_price
                auction.paid_for = True
                if request.user.id: #logged in user used buy it now
                    auction.current_bidder = request.user
                    #TODO upate item.buyer
                else:
                    auction.current_bidder = None #change when we create accounts for buy-now people
                auction.save()
                return HttpResponseRedirect('/success/')
            except stripe.CardError:
                context = {'error_message':"Your credit card was declined."}
                #return HttpResponseRedirect('/auction/'+str(auction.id))
                return HttpResponseRedirect('/')

          else: #Place a bid
            #TODO update item.buyer
            form = BidForm(request.POST, auction=auctionid)
            if request.user.is_authenticated():
                if form.is_valid():
                    bid = form.cleaned_data['bid']
                    auction.current_bid = bid
                    auction.current_bidder = request.user
                    if bid * Decimal(1.0999) > auction.buy_now_price:
                        auction.buy_now_price = bid * Decimal(1.1000000)
                    auction.save()
                    return HttpResponseRedirect('/auction/'+str(auction.id))
            else: #unauthenticated user. Redirect to login page, then bring 'em back here.
                  #TODO Figure out how to set next variable in context so manual url isnt needed
                  #TODO If they sign up through this chain of events, bring them back here
                return HttpResponseRedirect('/accounts/login/?next=/auction/'+str(auction.id))

    default_bid = auction.current_bid + Decimal(1.00)
    form = BidForm(initial={'bid':default_bid}) #prepopulate bid with $1.00 above current bid
    item = auction.item
    if auction.end_date < datetime.datetime.now():
        over = 1
    else:
        over = 0
    time_left = auction.end_date - datetime.datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    amount = int(auction.buy_now_price * 100)
    stripe_amount = json.dumps(amount)
    item_json = json.dumps(item.title)
    context = {'auction':auction, 'form':form,'item':item, 'days':days,'hours':hours,'minutes':minutes,'seconds':seconds,
               'amount':stripe_amount, 'over': over}
    return render(request, 'auction_detail.html', context)

#Shows all outstanding, unpaid auctions for user
@login_required
def pending(request):
    #find auctions where user is the highest bidder, payment has not been received, and have already ended
    now = datetime.datetime.now()
    user = request.user
    items = []
    auctions = Auction.objects.filter(current_bidder=user).filter(paid_for=False).filter(end_date__lt=now)
    for auction in auctions:
        items.append(auction.item)
    return render(request, 'pending.html', {'items':items})

#uses stripe checkout for user to pay for auction once bidding ends
@login_required
def pay(request, auctionid):
    auction = get_object_or_404(Auction, pk=auctionid)
    item = auction.item
    if request.user.id is not auction.current_bidder.id: #user is trying to pay for someone else's auction
        raise PermissionDenied
    if auction.paid_for: #user already paid for item
        return render(request, 'expired.html')
    if request.method == 'POST':
        token = request.POST.get('stripeToken', False)
        if token: #Successfully submitted Stripe
            stripe.api_key = test_secret_key()
            #email = request.POST['stripeEmail']
            amount_in_cents = int(auction.current_bid * 100)
            try:
                charge = stripe.Charge.create(
                    amount = amount_in_cents,
                    currency = "usd",
                    source = token,
                    description = "Circa Sale " + str(auctionid) + ": " + str(auction.item.title)
                )
                item.buyer = request.user
                auction.paid_for = True
                auction.save()
                item.save()
                return HttpResponseRedirect('/pending/')

            except stripe.CardError:
                raise Exception
                context = {'error_message':"Your credit card was declined."}
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/sell/')
    elapsed = datetime.datetime.now() - auction.end_date
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    amount = int(auction.current_bid * 100)
    stripe_amount = json.dumps(amount)
    context = {'days': days, 'hours':hours, 'minutes': minutes, 'auction':auction, 'amount':stripe_amount, 'item':item}
    return render(request, 'pay.html', context)

def success(request):
    return render(request, 'success.html')

def help(request):
    return render(request, 'help.html')

#remove from production
def todo(request):
    return render(request,'todo.html')