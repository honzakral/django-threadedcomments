from django.db import models

try:
    from django.urls import reverse  # Django 1.10+
except ImportError:
    from django.core.urlresolvers import reverse


class Message(models.Model):
    title = models.CharField(max_length=140)
    text = models.TextField()

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('message_detail', args=(self.pk,))
