from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from image_cropping import ImageCropField, ImageRatioField
# Create your models here.

class Auction(models.Model):
    SHORT = 3
    MEDIUM = 5
    LONG = 7
    DURATION_CHOICES = ((SHORT, '3 days'), (MEDIUM, '5 days'), (LONG, '7 days'),)

    starting_bid = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    current_bid = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    buy_now_price = models.DecimalField(max_digits=6, decimal_places=2, default=1.10)
    start_date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=MEDIUM)  # choices
    end_date = models.DateTimeField(null=True)
    current_bidder = models.ForeignKey(User, null=True, blank=True)
    buy_now_email = models.EmailField(blank=True, null=True)  # temporary field until we create users from buy now purchases
    zipcode = models.IntegerField(default=0)
    paid_for = models.BooleanField(default=False)

    def __str__(self):
        return str(self.end_date)

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    photo = ImageCropField(blank=True, upload_to='uploaded_images')
    cropping = ImageRatioField('photo', '225x225')
    auction = models.OneToOneField(Auction, null=True)
    seller = models.ForeignKey(User, related_name='seller_profile', null=True)  # many items per one seller
    buyer = models.ForeignKey(User, related_name='buyer_profile', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.seller is not None and self.buyer is not None and self.seller == self.buyer:
            raise IntegrityError('seller cannot also be the buyer')
        else:
            super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alt_id = models.TextField(default=None)  # Braintree?
    rating = models.DecimalField(max_digits=4, decimal_places=2, blank=True, default=0.0)
    num_reviews = models.IntegerField(default=0)
    address = models.TextField(null=True, blank=True)
    zipcode = models.IntegerField(default=0)
