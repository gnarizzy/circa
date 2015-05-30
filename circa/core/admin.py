from django.contrib import admin
from core.models import Item, Listing, UserProfile
from image_cropping import ImageCroppingMixin

class ItemAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(Item, ItemAdmin)
admin.site.register(Listing)
admin.site.register(UserProfile)