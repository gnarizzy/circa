from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from core.models import Item, Auction
from core.forms import ItemForm
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

            #redirect to auction page so they can fill auction data

            #if form has errors?
    else:
        form = ItemForm()
    context = {}
    return render(request,'sell.html',{'form':form})

def auction(request, itemid):
    item = get_object_or_404(Item, pk=itemid)
    return HttpResponse(item.title)

def todo(request):
    return render(request,'todo.html')