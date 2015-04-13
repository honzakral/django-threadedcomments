import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from django.apps import apps
except ImportError:
    # Django 1.6 or below.
    def is_installed(appname):
        return appname in settings.INSTALLED_APPS
else:
    # Django 1.7 provides an official API, and INSTALLED_APPS may contain non-string values too.
    # However, by checking for settings.INSTALLED_APPS the check can occur before the app registry is ready.
    def is_installed(appname):
        return appname in settings.INSTALLED_APPS #or apps.is_installed(appname)


if is_installed('django.contrib.comments'):
    BASE_APP = 'django.contrib.comments'
    if django.VERSION >= (1,8):
        # Help users migrate their projects easier without having to debug our import errors.
        # The django-contrib-comments package is already installed via setup.py, so changing INSTALLED_APPS is enough.
        raise ImproperlyConfigured("Django 1.8 no longer provides django.contrib.comments.\nUse 'django_comments' in INSTALLED_APPS instead.")

    # Django 1.7 and below
    from django.contrib import comments as django_comments
    from django.contrib.comments import get_model, get_form, signals
    from django.contrib.comments.forms import CommentForm
    from django.contrib.comments.models import Comment
    from django.contrib.comments.managers import CommentManager
    from django.contrib.comments.views.comments import CommentPostBadRequest
elif is_installed('django_comments'):
    BASE_APP = 'django_comments'
    # as of Django 1.8, this is a separate app.
    import django_comments
    from django_comments import get_model, get_form, signals
    from django_comments.forms import CommentForm
    from django_comments.models import Comment
    from django_comments.managers import CommentManager
    from django_comments.views.comments import CommentPostBadRequest
else:
    raise ImproperlyConfigured("Missing django_comments or django.contrib.comments in INSTALLED_APPS")


__all__ = (
    'BASE_APP',
    'is_installed',
    'django_comments',
    'signals',
    'get_model',
    'get_form',
    'CommentForm',
    'Comment',
    'CommentManager',
    'moderator',
    'CommentModerator',
    'CommentPostBadRequest',
)
