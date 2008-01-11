import os
DIRNAME = os.path.dirname(__file__)

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ":memory:"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'threadedcomments',
)