from django import forms
from decimal import *
from core.models import Item, Auction
from core.zipcode import zipcodes

class ItemForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100, help_text="Title")
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), help_text="Description")
    class Meta:
        model = Item
        fields = ('title', 'description')

class AuctionForm(forms.ModelForm):
    starting_bid = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control'}),)
    buy_now_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control'}),label = "Buy now price")
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}),label = "Pickup zipcode")

#Make sure starting bid is at least $1.00
    def clean_starting_bid(self):
        starting_bid = self.cleaned_data['starting_bid']
        if starting_bid < 1:
            raise forms.ValidationError("The minimum starting bid is $1.00.")
        return starting_bid

#Make sure buy now price is at least 10% greater than starting bid
    def clean_buy_now_price(self):
        try:
            starting_bid = self.cleaned_data['starting_bid']
        except KeyError: #starting_bid doesn't exist because it was invalid
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting bid, which must be at "
                                        "least $1.00")
        buy_now_price = self.cleaned_data['buy_now_price']

        if starting_bid * Decimal(1.0999) > buy_now_price:
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting bid.")

        return buy_now_price

    #make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip = self.cleaned_data['zipcode']
        if zip not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is not yet available in your zip code.")
        return zip

    class Meta:
        model = Auction
        fields = ('starting_bid', 'buy_now_price','duration', 'zipcode')


class BidForm (forms.Form):
    bid = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control'}),
                             label="Enter your bid", decimal_places = 2)
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}),
                                 label = "Enter your shipping zip code")


    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop('auction', None)
        super(BidForm, self).__init__(*args,**kwargs)

#check to make sure bid isn't higher than buy it now?

#make sure submitted bid is greater than current bid
    def clean_bid(self):
        bid = self.cleaned_data['bid']
        if self.auction:
            auction_bid = Auction.objects.get(pk=self.auction).current_bid
            if bid <= auction_bid:
                raise forms.ValidationError("Your bid must be greater than the current bid.")
        return bid

#make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip = self.cleaned_data['zipcode']
        if zip not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is not yet available in your zip code.")
        return zip

