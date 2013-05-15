from django.contrib import admin
from .models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'text',)

admin.site.register(Message, MessageAdmin)
