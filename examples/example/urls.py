import django_comments.urls
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from core import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^comments/', include(django_comments.urls)),

    url(r'^$', views.home, name='homepage'),
    url(r'^message/(?P<id>.+)$', views.message, name='message_detail'),
]
