from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from core.views import index
from social.exceptions import AuthCanceled


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return index(request)