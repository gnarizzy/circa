from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from core.models import Item, Auction
from core.forms import ItemForm, AuctionForm
from django.contrib.auth.models import User

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
            return HttpResponseRedirect('/auction/'+str(item.id))

            #if form has errors?
    else:
        form = ItemForm()
    return render(request,'sell.html',{'form':form})

#creating an auction for previously posted item
def auction(request, itemid):
    item = get_object_or_404(Item, pk=itemid)

    if request.method == 'POST':
        form = AuctionForm(request.POST)

    else:
        form = AuctionForm()

    context = {'item':item,'form':form}
    return render(request, 'create_auction.html', context)

#remove from production
def todo(request):
    return render(request,'todo.html')