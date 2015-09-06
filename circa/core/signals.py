from core.email import welcome_new_user_notification
from core.models import UserProfile
from django.dispatch import receiver
from registration.signals import user_registered


@receiver(user_registered)
def send_welcome_email(sender, **kwargs):
    user = kwargs['user']
    UserProfile.user_creation(user)
    welcome_new_user_notification(user)
