from django import forms
from decimal import *

from core.models import Item, Auction

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'description','photo1','photo2','photo3',)

class AuctionForm(forms.ModelForm):
    starting_bid = forms.DecimalField(label = "Starting bid")
    buy_now_price = forms.DecimalField(label = "Buy now price")

#Make sure starting bid is at least $1.00
    def clean_starting_bid(self):
        starting_bid = self.cleaned_data['starting_bid']
        if starting_bid < 1:
            raise forms.ValidationError("The minimum starting bid is $1.00.")
        return starting_bid

#Make sure buy now price is at least 10% greater than starting bid
    def clean_buy_now_price(self):
        starting_bid = self.cleaned_data['starting_bid']
        buy_now_price = self.cleaned_data['buy_now_price']

        if starting_bid * Decimal(1.0999) > buy_now_price:
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting bid.")

        return buy_now_price

    class Meta:
        model = Auction
        fields = ('starting_bid', 'buy_now_price',) #add duration once choices issue is fixed