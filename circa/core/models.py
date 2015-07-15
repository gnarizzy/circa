from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from image_cropping import ImageCropField, ImageRatioField
# Create your models here.

class Listing(models.Model):
    starting_offer = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    current_offer = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    buy_now_price = models.DecimalField(max_digits=6, decimal_places=2, default=5.50)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    current_offer_user = models.ForeignKey(User, null=True, blank=True)
    buy_now_email = models.EmailField(blank=True, null=True)  # temporary field until we create users from buy now purchases
    zipcode = models.IntegerField(default=0)
    paid_for = models.BooleanField(default=False)
    payout = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.id)

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    photo = ImageCropField(upload_to='uploaded_images')
    cropping = ImageRatioField('photo', '225x225')
    listing = models.OneToOneField(Listing, null=True)
    seller = models.ForeignKey(User, related_name='seller_profile', null=True)  # Many items per one seller
    buyer = models.ForeignKey(User, related_name='buyer_profile', null=True, blank=True)

    UNCLASSIFIED = 0
    ELECTRONICS = 1
    BOOKS = 3
    SHOES = 4
    OTHER = 5
    VIDEO_GAMES = 6
    CATEGORY_CHOICES = (
        (UNCLASSIFIED, '-- Please Pick a Category --'),
        (BOOKS, 'Books'),
        (ELECTRONICS, 'Electronics'),
        (SHOES, 'Shoes'),
        (VIDEO_GAMES, 'Video Games'),
        (OTHER, 'Other')
    )
    CATEGORY_NAMES = {
        'electronics': ELECTRONICS,
        'books': BOOKS,
        'shoes': SHOES,
        'videogames': VIDEO_GAMES,
        'other': OTHER
    }
    category = models.IntegerField(choices=CATEGORY_CHOICES, default=UNCLASSIFIED)

    def save(self, *args, **kwargs):
        if self.seller is not None and self.buyer is not None and self.seller == self.buyer:
            raise IntegrityError('seller cannot also be the buyer')
        else:
            super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Address(models.Model):
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    address = models.OneToOneField(Address, null=True, blank=True)

    def __str__(self):
        return self.user.username

class PromoCode(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        return self.code
