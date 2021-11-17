#!/usr/bin/env python
from importlib import import_module
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
from os import path


# Give feedback on used versions
sys.stderr.write(f'Using Python version {sys.version[:5]} from {sys.executable}\n')
sys.stderr.write('Using Django version {} from {}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'django_comments',
            'threadedcomments',
        ),
        MIDDLEWARE = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        SITE_ID = 1,
        SECRET_KEY="testtest",
        STATIC_URL="/static/",
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
        # App settings
        COMMENTS_APP = 'threadedcomments',
        COMMENTS_ALLOW_PROFANITIES = True,
    )

def runtests():
    argv = sys.argv[:1] + ['test', 'threadedcomments', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
