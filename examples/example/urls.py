from django.conf.urls import *
from django.contrib import admin

# Enable the admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include(
        'django.contrib.comments.urls')),

    url(r'^$', 'core.views.home', name='homepage'),
    url(r'^message/(?P<id>.+)$',
        'core.views.message', name='message_detail'),
)
