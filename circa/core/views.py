from django.shortcuts import render
from django.http import HttpResponse
from core.models import Item
from core.forms import ItemForm

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
            form.save(commit=True)

            #redirect to auction page so they can fill auction data

            #if form has errors?

    else:
        form = ItemForm()
    context = {}
    return render(request,'sell.html',{'form':form})

def todo(request):
    return render(request,'todo.html')