from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Item(models.Model):
    description = models.TextField(default='')

class Auction(models.Model):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alt_id = models.TextField(default=None) #Stripe
    rating = models.DecimalField(max_digits = 4, decimal_places=2)
    num_reviews = models.IntegerField()
