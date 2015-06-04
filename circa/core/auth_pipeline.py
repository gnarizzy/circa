from core.email import welcome_new_user_notification

def send_welcome_email_social_auth(**kwargs):
    if kwargs['is_new'] and kwargs['details']['email']:
        welcome_new_user_notification(kwargs['details']['email'])
