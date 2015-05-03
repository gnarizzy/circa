from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from core.models import Item, Auction
from core.forms import ItemForm, AuctionForm, BidForm
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

def auction_detail(request, auctionid):
    auction = get_object_or_404(Auction, pk=auctionid)

    if request.method == 'POST':
          token = request.POST.get('stripeToken', False)
          if token: #Buy Now
            stripe.api_key = "sk_live_NPgcsO9rTjNWGOYs83SMqqx0"
            email = request.POST['stripeEmail']
            amount_in_cents = int(auction.buy_now_price * 100)
            try:
                charge = stripe.Charge.create(
                    amount = amount_in_cents,
                    currency = "usd",
                    source = token,
                    description = "Circa Buy Now: " + str(auction.item.title)
                )
                auction.buy_now_email = email
                auction.end_date = datetime.datetime.now()
                auction.current_bid = auction.buy_now_price
                auction.paid_for = True
                if request.user.id: #logged in user used buy it now
                    auction.current_bidder = request.user
                else:
                    auction.current_bidder = None #change when we create accounts for buy-now people
                auction.save()
            except stripe.CardError:
                context = {'error_message':"Your credit card was declined."}
                return HttpResponseRedirect('/auction/'+str(auction.id))
            return HttpResponseRedirect('/success/')
          else: #Place a bid
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

#Shows all outstanding payments and uses stripe checkout to pay
@login_required
def pay(request):
    #find auctions where user is the highest bidder, payment has not been received, and have already ended
    now = datetime.datetime.now()
    items = []
    auctions = Auction.objects.filter(current_bidder=request.user).filter(paid_for=False).filter(end_date__lt=now)
    for auction in auctions:
        items.append(auction.item)
    return render(request, 'pay.html', {'items':items})

def success(request):
    return render(request, 'success.html')

def help(request):
    return render(request, 'help.html')

#remove from production
def todo(request):
    return render(request,'todo.html')