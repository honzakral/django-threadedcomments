from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.admin import CommentsAdmin

from threadedcomments.models import ThreadedComment

def remove_comment(modeladmin, request, queryset):
    queryset.update(is_removed=True)
remove_comment.short_description = _("Mark selected comments as removed")
 
def un_remove_comment(modeladmin, request, queryset):
    queryset.update(is_removed=False)
un_remove_comment.short_description = _("Mark selected comments as not removed")
 
def public_comment(modeladmin, request, queryset):
    queryset.update(is_public=True)
public_comment.short_description = _("Mark selected comments as published")
 
def un_public_comment(modeladmin, request, queryset):
    queryset.update(is_public=False)
un_public_comment.short_description = _("Mark selected comments as unpublished")
 
 

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

    list_display = ('name', 'title', 'content_type', 'object_pk', 'parent', 'ip_address', 'submit_date', 'is_public', 'is_removed')
    search_fields = ('title', 'comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address')
    raw_id_fields = ("parent",)
    actions = CommentsAdmin.actions + [remove_comment, un_remove_comment, public_comment, un_public_comment]

admin.site.register(ThreadedComment, ThreadedCommentsAdmin)

