import os

from django.conf.urls.defaults import patterns, include, handler500, handler404

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

ROOT_URLCONF = 'settings'

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.comments',
    'threadedcomments',
)

COMMENTS_APP = 'threadedcomments'

urlpatterns = patterns('',
    (r'^comments/', include('django.contrib.comments.urls')),
)