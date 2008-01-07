from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    ### Comments ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.comment, name="tc_post_comment"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.comment, name="tc_post_free_comment"),
    
    ### Comments (AJAX) ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>ajax)/$', views.comment, name="tc_post_comment_ajax"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>ajax)/$', views.comment, name="tc_post_free_comment_ajax"),

    ### Free Comments ###
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.free_comment, name="tc_post_free_comment"),
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.free_comment, name="tc_post_free_comment"),

    ### Free Comments (AJAX) ###
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>ajax)/$', views.free_comment, name="tc_post_free_comment_ajax"),
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>ajax)/$', views.free_comment, name="tc_post_free_comment_ajax"),
    
    ### Voting ###
    url(r'^vote/(?P<comment>\d+)/(?P<vote>up|down)/$', views.vote, name="tc_post_form"),
        
    ### Voting (AJAX) ###
    url(r'^vote/(?P<comment>\d+)/(?P<vote>up|down)/(?P<ajax>ajax)/$', views.vote, name="tc_post_form_ajax"),
    
    ### Free Voting ###
    url(r'^freevote/(?P<comment>\d+)/(?P<vote>up|down)/$', views.vote, {'free' : True}, name="tc_post_form"),
        
    ### Free Voting (AJAX) ###
    url(r'^freevote/(?P<comment>\d+)/(?P<vote>up|down)/(?P<ajax>ajax)/$', {'free' : True}, views.vote, name="tc_post_form_ajax"),
)