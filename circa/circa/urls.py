from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^todo/','core.views.todo', name= 'todo'),
    url(r'^sell/','core.views.sell', name= 'sell'),
    url(r'^auction/(?P<itemid>\d+)/$','core.views.auction',name= 'auction'),
    url(r'^$', 'core.views.index', name='index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
