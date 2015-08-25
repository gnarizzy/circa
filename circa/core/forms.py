from core.models import Item, Listing, PromoCode, Address, UserProfile
from core.zipcode import zipcodes
from datetime import datetime, timedelta
from decimal import *
from django import forms
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions

from io import BytesIO
from PIL import Image


class ItemListingForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate'}), label="Title", max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
                                  label="Description")
    category = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Item.CATEGORY_CHOICES)
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'validate'}), label='Buy now price')
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'validate'}), label='Pickup zipcode')

    # For image cropping purposes
    crop_x = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'crop-params'}))
    crop_y = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'crop-params'}))
    crop_height = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'crop-params'}))
    crop_width = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'crop-params'}))

    # Make sure starting offer is at least $5.00
    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 5:
            raise forms.ValidationError("The minimum price is $5.00.")
        return price

    # Make sure a category is chosen
    def clean_category(self):
        category = self.cleaned_data['category']
        if category is '0':
            raise forms.ValidationError("You must choose a category for your item.")
        return category

    # Make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip_code = self.cleaned_data['zipcode']
        if zip_code not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is not yet available in that zip code.")
        return zip_code

    def clean_crop_width(self):
        width = int(self.cleaned_data['crop_width'])
        height = int(self.cleaned_data['crop_height'])

        if width < 450 or height < 450:
            raise forms.ValidationError("Your cropped image must be at least 450 by 450.")
        return width

    def __init__(self, *args, **kwargs):
        self.seller = kwargs.pop('seller')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        item = super().save(commit=False)
        self.process_image(item)
        listing = Listing.objects.create(
            price=self.cleaned_data['price'],
            zipcode=self.cleaned_data['zipcode']
        )
        item.listing = listing
        item.seller = self.seller
        item.save()
        return item

    def process_image(self, item):
        image = Image.open(item.photo)

        left = int(self.cleaned_data['crop_x'])
        top = int(self.cleaned_data['crop_y'])
        width = int(self.cleaned_data['crop_width'])
        height = int(self.cleaned_data['crop_height'])

        box = (left, top, left+width, top+height)
        image = image.crop(box)
        f = BytesIO()
        try:
            image.save(f, format='jpeg')
            s = f.getvalue()
            item.photo.save(item.photo.name, ContentFile(s))

        finally:
            f.close()

    class Meta:
        model = Item
        fields = {'title', 'description', 'category', 'photo'}




class PromoForm(forms.Form):
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Grabs current user
        self.listing = kwargs.pop('listing')  # Grabs listing
        super(PromoForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        found = False
        promo_code = self.cleaned_data['code']

        if PromoCode.objects.all().count() == 0:
            raise forms.ValidationError("Sorry, that code isn't valid.")

        codes = PromoCode.objects.all()

        for promotional_code in codes:

            if promotional_code.code == promo_code:
                if promotional_code.redeemed:
                    raise forms.ValidationError("Sorry, promo code already used.")

                elif promotional_code.user != self.user:
                    raise forms.ValidationError("Sorry, that's not your code!")

                else:
                    found = True
                    break

        if not found:
            raise forms.ValidationError("Sorry, that code is not valid.")

        return promo_code

    def save(self):
        promo = PromoCode.objects.filter(code=self.cleaned_data['code'])[0]
        promo.listing = self.listing
        promo.save()
        self.listing.save()


class AddressForm(forms.Form):
    address_line_1 = forms.CharField()
    address_line_2 = forms.CharField(required=False)
    city = forms.CharField()

    # Must be changed when we branch to different states!
    state = forms.CharField(widget=forms.HiddenInput())
    INITIAL_STATE = 'GA'

    zipcode = forms.CharField()
    special_instructions = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self):
        if not hasattr(self.user, 'userprofile'):
            UserProfile.objects.create(user=self.user)

        address = Address.objects.create(
            address_line_1=self.cleaned_data['address_line_1'],
            address_line_2=self.cleaned_data['address_line_2'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zipcode=self.cleaned_data['zipcode'],
            special_instructions=self.cleaned_data['special_instructions']
        )
        self.user.userprofile.address = address
        self.user.userprofile.save()


class EditListingForm(forms.Form):
    # Information for Item
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate'}), label="Title", max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
                                  label="Description")
    category = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Item.CATEGORY_CHOICES)

    # Information for Listing
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'validate'}))
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'validate'}), label='Pickup zipcode')

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing')  # Grabs current listing
        super(EditListingForm, self).__init__(*args, **kwargs)

    # Make sure starting offer is at least $5.00, and that no offers have yet been made
    def clean_price(self):
        price = Decimal(self.cleaned_data['price'])
        if price < 5:
            raise forms.ValidationError("The minimum price is $5.00.")
        return price

    # Make sure a category is chosen
    def clean_category(self):
        category = self.cleaned_data['category']
        if category is '0':
            raise forms.ValidationError("You must choose a category for your item.")
        return category

    # make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip_code = self.cleaned_data['zipcode']
        if zip_code not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is not yet available in that zip code.")
        return zip_code

    def save(self):
        self.listing.item.title = self.cleaned_data['title']
        self.listing.item.description = self.cleaned_data['description']
        self.listing.item.category = self.cleaned_data['category']
        self.listing.price = self.cleaned_data['price']
        self.listing.zipcode = self.cleaned_data['zipcode']

        self.listing.item.save()
        self.listing.save()
