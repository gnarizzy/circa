from django.dispatch import receiver
from core.email import welcome_new_user_notification
from registration.signals import user_registered

@receiver(user_registered)
def send_welcome_email(sender, **kwargs):
    welcome_new_user_notification(kwargs['user'])
