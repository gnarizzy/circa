from django.conf.urls import patterns, include, url
from django.conf import settings # New Import
from django.conf.urls.static import static # New Import

from django.contrib import admin
from registration.backends.simple.views import RegistrationView

class MyRegistrationView(RegistrationView):
    def get_success_url(self,request, user):
        url = request.GET.get('next')
        if url:
            return url
        else:
            return '/'

urlpatterns = patterns('',
    # Examples:
    url(r'^todo/','core.views.todo', name= 'todo'),
    url(r'^sell/','core.views.sell', name= 'sell'),
    url(r'^createauction/(?P<itemid>\d+)/$','core.views.create_auction',name= 'create_auction'),
    url(r'^auction/(?P<auctionid>\d+)/$','core.views.auction_detail',name= 'auction_detail'),
    url(r'^$', 'core.views.index', name='index'),
    url(r'^success/', 'core.views.success',name='success'),
    url(r'^help/', 'core.views.help',name='help'),
    url(r'^pending/', 'core.views.pending', name='pending'),
    url(r'^pay/(?P<auctionid>\d+)/$', 'core.views.pay', name = 'pay'),
    url(r'^connect/', 'core.views.connect', name='connect'),
    #url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    (r'^accounts/', include('registration.backends.simple.urls')),
)
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )


if not settings.DEBUG:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)