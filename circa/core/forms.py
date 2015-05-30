from core.models import Item, Listing
from core.zipcode import zipcodes
from decimal import *
from django import forms

class ItemForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Item
        fields = ('title', 'description', 'photo')

class ListingForm(forms.ModelForm):
    starting_offer = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}),)
    buy_now_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Buy now price')
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Pickup zipcode')

    # Make sure starting bid is at least $1.00
    def clean_starting_offer(self):
        starting_offer = self.cleaned_data['starting_offer']
        if starting_offer < 1:
            raise forms.ValidationError("The minimum starting bid is $1.00.")
        return starting_offer

    # Make sure buy now price is at least 10% greater than starting bid
    def clean_buy_now_price(self):
        try:
            starting_offer = self.cleaned_data['starting_offer']
        except KeyError:  # starting_bid doesn't exist because it was invalid
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting bid, which must be at "
                                        "least $1.00")
        buy_now_price = self.cleaned_data['buy_now_price']

        if starting_offer * Decimal(1.0999) > buy_now_price:
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting bid.")

        return buy_now_price

    # make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip_code = self.cleaned_data['zipcode']
        if zip_code not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is not yet available in your zip code.")
        return zip_code

    class Meta:
        model = Listing
        fields = ('starting_offer', 'buy_now_price', 'zipcode')


class OfferForm (forms.Form):
    offer = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}),
                               label='Your offer', decimal_places=2)
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                 label='Zip code')

    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop('auction', None)
        super(OfferForm, self).__init__(*args,**kwargs)

    # check to make sure offer isn't higher than buy it now?

    # make sure submitted offer is greater than current offer
    def clean_offer(self):
        offer = self.cleaned_data['bid']
        if self.auction:
            auction_offer = Listing.objects.get(pk=self.auction).current_offer
            if offer <= auction_offer:
                raise forms.ValidationError("Your bid must be greater than the current bid.")
        return offer

    # make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip = self.cleaned_data['zipcode']
        if zip not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is only available in zips near Georgia Tech. Visit our "
                                        "help page to see which zipcodes are available.")
        return zip

