from core.models import Item, Listing, PromoCode
from core.zipcode import zipcodes
from decimal import *
from django import forms

class ItemForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate'}),label="Title", max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
                                  label="Description")

    class Meta:
        model = Item
        fields = ('title', 'description', 'photo')

class ListingForm(forms.ModelForm):
    starting_offer = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'validate'}),)
    buy_now_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'validate'}), label='Buy now price')
    zipcode = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'validate'}), label='Pickup zipcode')

    # Make sure starting offer is at least $5.00
    def clean_starting_offer(self):
        starting_offer = self.cleaned_data['starting_offer']
        if starting_offer < 5:
            raise forms.ValidationError("The minimum starting offer is $5.00.")
        return starting_offer

    # Make sure buy now price is at least 10% greater than starting offer
    def clean_buy_now_price(self):
        try:
            starting_offer = self.cleaned_data['starting_offer']
        except KeyError:  # starting_offer doesn't exist because it was invalid
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting offer, which must "
                                        "be at least $5.00")
        buy_now_price = self.cleaned_data['buy_now_price']

        if starting_offer * Decimal(1.0999) > buy_now_price:
            raise forms.ValidationError("Buy now price must be at least 10% higher than starting offer.")

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
        self.listing = kwargs.pop('listing', None) #Grabs current listing ID
        self.user = kwargs.pop('user', None) #Grabs current user
        super(OfferForm, self).__init__(*args,**kwargs)

    # check to make sure offer isn't higher than buy it now?

    # make sure submitted offer is greater than current offer
    def clean_offer(self):
        offer = self.cleaned_data['offer']
        if self.listing:
            listing_object = Listing.objects.get(pk=self.listing) #current listing

            if self.user and self.user.id is listing_object.item.seller.id: #user submitted offer on their own auction
                raise forms.ValidationError("Trying to submit an offer on your own item, eh? Seems legit.")


            listing_offer = listing_object.current_offer
            if not listing_offer: #no current offer, meaning no initial offer has been made
                if offer < Listing.objects.get(pk=self.listing).starting_offer:
                    raise forms.ValidationError("Your offer cannot be less than the asking price.")
            else:
                if offer <= listing_offer:
                    raise forms.ValidationError("Your offer must be greater than the current offer.")
        return offer

    # make sure shipping zip code is one we deliver to
    def clean_zipcode(self):
        zip = self.cleaned_data['zipcode']
        if zip not in zipcodes():
            raise forms.ValidationError("Unfortunately, Circa is only available in zips near Georgia Tech. Visit our "
                                        "help page to see which zipcodes are available.")
        return zip

class PromoForm (forms.Form):
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) #Grabs current user
        super(PromoForm, self).__init__(*args,**kwargs)

    def clean_code(self):
        found = False
        promo_code = self.cleaned_data['code']

        codes = PromoCode.objects.all()
        print("PREFORLOOP")
        for promotional_code in codes:
            print("FOR LOOP")
            print("PROMO_CODE is "+ promo_code)
            print("promotional_code is"+ promotional_code.code)
            print(promotional_code.code == promo_code)
            if promotional_code.code == promo_code:
                print("IF STATMENT")
                found = True
            else:
                print("ELSE STATEMENT")
                raise forms.ValidationError("Either that code has been redeemed, isn't valid, or isn't associated with your"
                                        " account. If this is a mistake, please email support@usecirca.com")
        return promo_code