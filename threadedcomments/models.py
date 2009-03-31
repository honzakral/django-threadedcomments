from django.db import models
from django.contrib.comments.models import Comment

class ThreadedComment(Comment):
    parent = models.ForeignKey('self', null=True, blank=True, default=None,
        related_name='children')
    level  = models.IntegerField(default=0)

    def save(self, force_insert=False, force_update=False):
        if self.parent:
            self.level = self.parent.level + 1
        super(ThreadedComment, self).save(force_insert=force_insert,
            force_update=force_update)
