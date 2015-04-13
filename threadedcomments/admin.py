from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .compat import BASE_APP
from .models import ThreadedComment

# This code is not in the .compat module to avoid admin imports in all other code.
# The admin import usually starts a model registration too, hence keep these imports here.

if BASE_APP == 'django.contrib.comments':
    # Django 1.7 and below
    from django.contrib.comments.admin import CommentsAdmin
elif BASE_APP == 'django_comments':
    # Django 1.8 and up
    from django_comments.admin import CommentsAdmin
else:
    raise NotImplementedError()


class ThreadedCommentsAdmin(CommentsAdmin):
    fieldsets = (
        (None,
           {'fields': ('content_type', 'object_pk', 'site')}
        ),
        (_('Content'),
           {'fields': ('user', 'user_name', 'user_email', 'user_url', 'title', 'comment')}
        ),
        (_('Hierarchy'),
           {'fields': ('parent',)}
        ),
        (_('Metadata'),
           {'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed')}
        ),
    )

    list_display = ('name', 'title', 'content_type', 'object_pk', 'parent',
                    'ip_address', 'submit_date', 'is_public', 'is_removed')
    search_fields = ('title', 'comment', 'user__username', 'user_name',
                     'user_email', 'user_url', 'ip_address')
    raw_id_fields = ("parent",)

admin.site.register(ThreadedComment, ThreadedCommentsAdmin)

