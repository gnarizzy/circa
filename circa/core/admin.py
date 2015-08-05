from django.contrib import admin
from core.models import Item, Listing, UserProfile, PromoCode, Address
from image_cropping import ImageCroppingMixin

class ItemAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(Item, ItemAdmin)
admin.site.register(Listing)
admin.site.register(UserProfile)
admin.site.register(PromoCode)
admin.site.register(Address)