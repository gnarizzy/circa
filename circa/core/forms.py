from django import forms

from core.models import Item, Auction

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'description','photo1','photo2','photo3',)

class AuctionForm(forms.ModelForm):
    starting_bid = forms.DecimalField(label = "Starting bid")
    buy_now_price = forms.DecimalField(label = "Buy now price")
    class Meta:
        model = Auction
        fields = ('starting_bid', 'buy_now_price', 'duration')