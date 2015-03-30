from django.shortcuts import render
from django.http import HttpResponse
from core.models import Item
# Create your views here.
def index(request):
    item_list = Item.objects.all()
    context = {'items':item_list}
    return render(request, 'index.html', context)

def todo(request):
    return render(request,'todo.html')