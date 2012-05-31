from django.db import models

class Message(models.Model):
    title   = models.CharField(max_length=140)
    text    = models.TextField()