try: #Django 1.5+
    from django.conf.urls import *
except: # Django 1.4.5 and lower
    from django.conf.urls.defaults import *
from django.contrib import admin

# Enable the admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include('django.contrib.comments.urls')),

    url(r'^$', 'core.views.home'),
    url(r'^message/(?P<id>.+)$', 'core.views.message', name='message_detail'),
)
