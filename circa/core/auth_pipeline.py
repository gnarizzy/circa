from core.email import welcome_new_user_fb_notification

def send_welcome_email_social_auth(**kwargs):
    if kwargs['is_new']:
        if kwargs['details']['email']:
            welcome_new_user_fb_notification(kwargs['details']['username'], kwargs['details']['email'])
        else:
            pass
            # panic
