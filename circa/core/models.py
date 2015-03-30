from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Auction(models.Model):
    current_bid = models.DecimalField(max_digits = 6, decimal_places = 2, default=1.00)

class Item(models.Model):
    title = models.TextField(default='')
    description = models.TextField(default='')
    photo1 = models.URLField()
    photo2 = models.URLField()
    photo3 = models.URLField()
    auction = models.OneToOneField(Auction)
    seller = models.OneToOneField(User, related_name ='seller_profile', default = None)
    buyer = models.OneToOneField(User, related_name = 'buyer_profile', default = None)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alt_id = models.TextField(default=None) #Stripe
    rating = models.DecimalField(max_digits = 4, decimal_places=2)
    num_reviews = models.IntegerField()
