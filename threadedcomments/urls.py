from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    ### Comments ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.comment, name="tc_comment"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.comment, name="tc_comment_parent"),
    
    ### Comments (AJAX) ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>json|xml)/$', views.comment, name="tc_comment_ajax"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>json|xml)/$', views.comment, name="tc_comment_parent_ajax"),

    ### Free Comments ###
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.free_comment, name="tc_free_comment"),
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.free_comment, name="tc_free_comment_parent"),

    ### Free Comments (AJAX) ###
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>json|xml)/$', views.free_comment, name="tc_free_comment_ajax"),
    url(r'^freecomment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>json|xml)/$', views.free_comment, name="tc_free_comment_parent_ajax"),
    
    ### Voting ###
    url(r'^vote/(?P<comment>\d+)/(?P<vote>up|down)/$', views.vote, name="tc_vote"),
        
    ### Voting (AJAX) ###
    url(r'^vote/(?P<comment>\d+)/(?P<vote>up|down)/(?P<ajax>json|xml)/$', views.vote, name="tc_vote_ajax"),
    
    ### Free Voting ###
    url(r'^freevote/(?P<comment>\d+)/(?P<vote>up|down)/$', views.vote, kwargs={'free' : True}, name="tc_free_vote"),
        
    ### Free Voting (AJAX) ###
    url(r'^freevote/(?P<comment>\d+)/(?P<vote>up|down)/(?P<ajax>json|xml)/$', views.vote, kwargs={'free' : True}, name="tc_free_vote_ajax"),
)