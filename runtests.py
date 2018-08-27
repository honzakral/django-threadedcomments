#!/usr/bin/env python
from importlib import import_module
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
from os import path


# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    if django.VERSION >= (2, 0):
        versioned_settings = dict(
            MIDDLEWARE = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            )
        )
    else:
        versioned_settings = dict(
            MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            )
        )

    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'django_comments',
            'threadedcomments',
        ),
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
        ],
        ROOT_URLCONF = 'django_comments.urls',
        TEST_RUNNER = 'django.test.runner.DiscoverRunner',
        SITE_ID = 1,
        COMMENTS_APP = 'threadedcomments',
        COMMENTS_ALLOW_PROFANITIES = True,
        **versioned_settings
    )

def runtests():
    argv = sys.argv[:1] + ['test', 'threadedcomments', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
