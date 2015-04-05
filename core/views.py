from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from core.models import Item, Auction
from core.forms import ItemForm, AuctionForm
from django.contrib.auth.models import User

import datetime

#home page
def index(request):
    item_list = Item.objects.all()
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
            HttpResponseRedirect('/auction/'+str(auction.id))

    else:
        form = AuctionForm()

    context = {'item':item,'form':form}
    return render(request, 'create_auction.html', context)

#Displays the requested auction along with info about auction item, or 404 page

def auction_detail(request, auctionid):
    auction = get_object_or_404(Auction, pk=auctionid)
    item = auction.item
    context = {'auction':auction, 'item':item}
    return render(request, 'auction_detail', context)


#remove from production
def todo(request):
    return render(request,'todo.html')