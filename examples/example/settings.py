# Django settings for example project.
#
# These settings are pretty basic.
# The only relevant settings are the defaults are:
# - INSTALLED_APPS
# - COMMENTS_APP
#
# And the following are configured to sane defaults:
# - STATIC_ROOT / STATIC_URL
# - MEDIA_ROOT / MEDIA_URL
#
import os
import django

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

#DEFAULT_FROM_EMAIL = 'your_email@domain.com'

# People who receive 404 errors
MANAGERS = ADMINS


# -- Server specific settings

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


# -- Internal Django config

# Language codes
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Paths, using autodetection
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

ROOT_URLCONF = 'example.urls'

# Only included for Django 1.3 users:
ADMIN_MEDIA_PREFIX = '/static/admin/'


# -- Plugin components

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
MIDDLEWARE = MIDDLEWARE_CLASSES  # Django 2.0

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = ()

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
)

if django.VERSION >= (1, 8):
    INSTALLED_APPS += ('django_comments',)
else:
    INSTALLED_APPS += ('django.contrib.comments',)


# --- App settings

COMMENTS_APP = 'threadedcomments'
