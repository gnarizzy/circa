from django.contrib import admin
from core.models import Item, Auction, UserProfile

admin.site.register(Item)
admin.site.register(Auction)
admin.site.register(UserProfile)