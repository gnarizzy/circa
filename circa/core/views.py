from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from core.models import Item, Auction
from core.forms import ItemForm, AuctionForm, BidForm
from django.contrib.auth.models import User
from django import forms
from decimal import *

import datetime

#home page that shows items with associated auctions that haven't already ended
def index(request):
    now = datetime.datetime.now()
    item_list = Item.objects.exclude(auction__isnull=True).exclude(auction__end_date__lte = now)\
        .order_by('auction__end_date')
    context = {'items':item_list}
    return render(request, 'index.html', context)

#posting an item
def sell(request):

    if request.method == 'POST':
        form = ItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=True)
            return HttpResponseRedirect('/createauction/'+str(item.id))

            #if form has errors?
    else:
        form = ItemForm()
    return render(request,'sell.html',{'form':form})

#creating an auction for previously posted item
def create_auction(request, itemid):
    item = get_object_or_404(Item, pk=itemid)

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
        form = BidForm(request.POST, auction=auctionid)
        if form.is_valid():
            bid = form.cleaned_data['bid']
            auction.current_bid = bid
            if bid * Decimal(1.0999) > auction.buy_now_price:
                auction.buy_now_price = bid * Decimal(1.1000000)
            auction.save()
            return HttpResponseRedirect('/auction/'+str(auction.id))
    else:
        default_bid = auction.current_bid + Decimal(1.00)
        form = BidForm(initial={'bid':default_bid}) #prepopulate bid with $1.00 above current bid
    message = request.GET.get('message')
    item = auction.item
    time_left = auction.end_date - datetime.datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    context = {'auction':auction, 'form':form,'item':item, 'days':days,'hours':hours,'minutes':minutes,'seconds':seconds}
    return render(request, 'auction_detail.html', context)


#remove from production
def todo(request):
    return render(request,'todo.html')