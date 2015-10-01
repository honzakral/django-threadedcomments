from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

# Enable the admin
admin.autodiscover()

if 'django_comments' in settings.INSTALLED_APPS:
    # Django 1.7/1.8 situation
    COMMENT_URLS = 'django_comments.urls'
else:
    # Old Django projects
    COMMENT_URLS = 'django.contrib.comments.urls'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include(COMMENT_URLS)),

    url(r'^$', 'core.views.home', name='homepage'),
    url(r'^message/(?P<id>.+)$', 'core.views.message', name='message_detail'),
]
