from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from core import views

if 'django_comments' in settings.INSTALLED_APPS:
    # Django 1.7/1.8 situation
    import django_comments.urls
    COMMENT_URLS = django_comments.urls
else:
    # Old Django projects
    import django.contrib.comments.urls
    COMMENT_URLS = django.contrib.comments.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include(COMMENT_URLS)),

    url(r'^$', views.home, name='homepage'),
    url(r'^message/(?P<id>.+)$', views.message, name='message_detail'),
]
