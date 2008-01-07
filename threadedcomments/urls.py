from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^post_comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.post_comment, name="tc_post_comment"),
    url(r'^post_comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.post_comment, name="tc_post_comment"),
    url(r'^post_vote/(?P<comment>\d+)/(?P<vote>up|down)/$', views.post_vote, name="tc_post_form"),
)