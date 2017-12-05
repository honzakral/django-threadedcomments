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
    if django.VERSION >= (1,8):
        base_app = 'django_comments'

        versioned_settings = dict(
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
        )
    else:
        base_app = 'django.contrib.comments'
        versioned_settings = dict(
            TEMPLATE_LOADERS = (
                'django.template.loaders.app_directories.Loader',
            ),
            TEMPLATE_CONTEXT_PROCESSORS = list(default_settings.TEMPLATE_CONTEXT_PROCESSORS) + [
                'django.core.context_processors.request',
            ],
        )

    if django.VERSION >= (2, 0):
        versioned_settings.update(dict(
            MIDDLEWARE = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            )
        ))
    else:
        versioned_settings.update(dict(
            MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
            )
        ))

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
            base_app,
            'threadedcomments',
        ),
        ROOT_URLCONF = '{0}.urls'.format(base_app),
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner' if django.VERSION < (1,6) else 'django.test.runner.DiscoverRunner',
        SITE_ID = 1,
        COMMENTS_APP = 'threadedcomments',
        COMMENTS_ALLOW_PROFANITIES = True,
        **versioned_settings
    )

    sys.stderr.write('Using comments app {0} from {1}\n'.format(base_app, path.dirname(import_module(base_app).__file__)))

def runtests():
    argv = sys.argv[:1] + ['test', 'threadedcomments', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
