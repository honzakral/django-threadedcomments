from django.contrib import admin
from core.models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'text',)

admin.site.register(Message, MessageAdmin)
