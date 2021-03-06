from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.utils.text import slugify

from core.keys import secret_key

import stripe


class Listing(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    zipcode = models.IntegerField(default=0)
    paid_for = models.BooleanField(default=False)
    payout = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    address_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    photo = models.ImageField(upload_to='uploaded_images')
    listing = models.OneToOneField(Listing, null=True)
    seller = models.ForeignKey(User, related_name='seller_profile', null=True)  # Many items per one seller
    buyer = models.ForeignKey(User, related_name='buyer_profile', null=True, blank=True)
    slug = models.SlugField()

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
        if not self.id:
            # Newly created object, so create slug. This ensures if title changes there are no broken links
            self.slug = slugify(self.title)
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
    special_instructions = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.address_line_1)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    address = models.OneToOneField(Address, null=True, blank=True)

    @staticmethod
    def user_creation(user):
        UserProfile.objects.create(user=user)

    def __str__(self):
        return self.user.username


class PromoCode(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    value = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    listing = models.ForeignKey(Listing, blank=True, null=True)
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        return self.code
