from core.email import welcome_new_user_fb_notification
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from social.pipeline.partial import partial

@partial
def send_welcome_email_social_auth(strategy, backend, request, details, *args, **kwargs):
    if kwargs['is_new'] and details['email']:
        welcome_new_user_fb_notification(details['username'], details['email'])

    elif not details['email']:
        username = details['username'].replace(' ', '')
        user = User.objects.get(username=username)
        if user.email is '' and not request.get('email', None):
            return HttpResponseRedirect('/request_email')

        elif user.email is '' and request.get('email', None):
            welcome_new_user_fb_notification(details['username'], request['email'])
            return {'email': request['email']}

        return
