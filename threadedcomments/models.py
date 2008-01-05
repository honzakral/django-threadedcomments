from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from datetime import datetime

class ThreadedCommentManager(models.Manager):
    pass

class ThreadedComment(models.Model):
    # Generic Foreign Key Stuff
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    # Hierarchy Stuff
    parent = models.ForeignKey('self', null=True, default=None, related_name='children')
    
    # Meat n' Potatoes
    user = models.ForeignKey(User)
    date_submitted = models.DateTimeField(default = datetime.now)
    date_modified = models.DateTimeField(default = datetime.now)
    date_approved = models.DateTimeField(default = datetime.now)
    comment = models.TextField()
    is_public = models.BooleanField(default = True)
    is_approved = models.BooleanField(default = True)
    ip_address = models.IPAddressField()
    
    def _get_score(self):
        score = 0
        for vote in self.votes.all():
            score = score + vote.vote
        return score
    score = property(_get_score)
    
    objects = ThreadedCommentManager()
    
    def __unicode__(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment[:50]
    
    def save(self):
        self.date_modified = datetime.now()
        super(ThreadedComment, self).save()

class Vote(models.Model):
    VOTE_CHOICES = (('+1', +1),('-1', -1))
    
    user = models.ForeignKey(User)
    comment = models.ForeignKey(ThreadedComment, related_name = 'votes')
    vote = models.IntegerField(choices=VOTE_CHOICES)