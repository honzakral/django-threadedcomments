# Django settings for example project.
#
# These settings are pretty basic.
# The only relevent settings are the defaults are:
# - INSTALLED_APPS
# - COMMENTS_APP
#
# And the following are configured to sane defaults:
# - TEMPLATE_CONTEXT_PROCESSORS
# - STATIC_ROOT / STATIC_URL
# - MEDIA_ROOT / MEDIA_URL
#
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

#DEFAULT_FROM_EMAIL = 'your_email@domain.com'

# People who receive 404 errors
MANAGERS = ADMINS


## -- Server specific settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'sampledb.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'sfm=0t(!sqi&!y%66+e+#4m$1o&l%(l(w#vz$=_0c$5+#m*9yk'
SITE_ID = 1


## -- Internal Django config

# Language codes
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Paths, using autodetection
PROJECT_DIR  = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

ROOT_URLCONF = 'example.urls'

# Only included for Django 1.3 users:
ADMIN_MEDIA_PREFIX = '/static/admin/'


## -- Plugin components

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',    # Very useful to have, not found in default Django setup.
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_DIRS = ()

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Messages setup:
    'core',
    'threadedcomments',
    'django.contrib.comments',
)


## --- App settings

COMMENTS_APP = 'threadedcomments'
