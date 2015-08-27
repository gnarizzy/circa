from core.email import welcome_new_user_fb_notification
from core.models import UserProfile
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from social.pipeline.partial import partial

@partial
def setup_user_account(strategy, backend, request, details, *args, **kwargs):
    username = details['username'].replace(' ', '')
    user = User.objects.get(username=username)

    # New user supplied email and is new
    if kwargs['is_new'] and details['email']:
        UserProfile.objects.create(user=user)
        welcome_new_user_fb_notification(details['username'], details['email'])

    elif not details['email']:
        if user.email is '' and not request.get('email', None):
            return HttpResponseRedirect('/request_email')

        elif user.email is '' and request.get('email', None):
            user.email = request['email']
            user.save()
            UserProfile.objects.create(user=user)
            welcome_new_user_fb_notification(details['username'], request['email'])
            return {'email': request['email']}

    return
