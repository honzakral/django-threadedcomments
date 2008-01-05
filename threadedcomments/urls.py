from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^post_comment/$', views.post_comment, name="tc_post_comment"),
)