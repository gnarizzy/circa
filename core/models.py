from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
# Create your models here.

class Auction(models.Model):
    SHORT = datetime.timedelta(days=1)
    MEDIUM = datetime.timedelta(days=3)
    LONG = datetime.timedelta(days=5)
    DURATION_CHOICES = ((SHORT, '1 day'),(MEDIUM, '3 days'), (LONG, '5 days'),)

    starting_bid = models.DecimalField(max_digits = 6, decimal_places = 2, default=1.00)
    current_bid = models.DecimalField(max_digits = 6, decimal_places = 2, null = True)
    buy_now_price = models.DecimalField(max_digits = 6, decimal_places = 2, default = 1.10)
    start_date = models.DateTimeField(auto_now_add = True)
    duration = models.DurationField(default = MEDIUM) #choices
    end_date = models.DateTimeField(null = True)
    current_bidder = models.OneToOneField(User, null = True)

class Item(models.Model):
    title = models.TextField(default='')
    description = models.TextField(default='')
    photo1 = models.URLField(null = True)
    photo2 = models.URLField(null = True)
    photo3 = models.URLField(null = True)
    auction = models.OneToOneField(Auction, null = True)
    seller = models.OneToOneField(User, related_name ='seller_profile', null = True)
    buyer = models.OneToOneField(User, related_name = 'buyer_profile', null = True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alt_id = models.TextField(default=None) #Stripe
    rating = models.DecimalField(max_digits = 4, decimal_places=2)
    num_reviews = models.IntegerField()