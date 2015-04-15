from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Auction(models.Model):
    SHORT = 3
    MEDIUM = 5
    LONG = 7
    DURATION_CHOICES = ((SHORT, '3 days'),(MEDIUM, '5 days'), (LONG, '7 days'),)

    starting_bid = models.DecimalField(max_digits = 6, decimal_places = 2, default=1.00)
    current_bid = models.DecimalField(max_digits = 6, decimal_places = 2, null = True)
    buy_now_price = models.DecimalField(max_digits = 6, decimal_places = 2, default = 1.10)
    start_date = models.DateTimeField(auto_now_add = True)
    duration = models.IntegerField(choices = DURATION_CHOICES, default = MEDIUM) #choices
    end_date = models.DateTimeField(null = True)
    current_bidder = models.OneToOneField(User, null = True)
    zipcode = models.IntegerField(default = 0)

    def __str__(self):
        return str(self.end_date)

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    #photo1 = models.URLField(null = True)
    #photo2 = models.URLField(null = True)
    #photo3 = models.URLField(null = True)
    auction = models.OneToOneField(Auction, null = True)
    seller = models.ForeignKey(User, related_name ='seller_profile', null = True)
    buyer = models.OneToOneField(User, related_name = 'buyer_profile', null = True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alt_id = models.TextField(default=None) #Stripe
    rating = models.DecimalField(max_digits = 4, decimal_places=2)
    num_reviews = models.IntegerField()
    address = models.TextField(default=None)
    zipcode = models.IntegerField(default = 0)
