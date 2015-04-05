from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^todo/','core.views.todo', name= 'todo'),
    url(r'^sell/','core.views.sell', name= 'sell'),
    url(r'^createauction/(?P<itemid>\d+)/$','core.views.create_auction',name= 'create_auction'),
    url(r'^auction/(?P<auctionid>\d+)/$','core.views.auction_detail',name= 'auction_detail'),
    url(r'^$', 'core.views.index', name='index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
