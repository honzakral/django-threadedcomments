import django_comments.urls
from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comments/', include(django_comments.urls)),

    path('', views.home, name='homepage'),
    path('message/<path:id>', views.message, name='message_detail'),
]
