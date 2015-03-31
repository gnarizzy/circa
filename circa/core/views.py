from django.shortcuts import render
from django.http import HttpResponse
from core.models import Item

#home page
def index(request):
    item_list = Item.objects.all()
    context = {'items':item_list}
    return render(request, 'index.html', context)

#posting an item
def sell(request):
    context = {}
    return render(request,'sell.html',context)

def todo(request):
    return render(request,'todo.html')