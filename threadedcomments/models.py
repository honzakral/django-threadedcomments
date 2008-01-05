from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from datetime import datetime

class ThreadedCommentManager(models.Manager):
    def get_tree(self, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        comments = list(self.get_query_set().filter(
            content_type = content_type,
            object_id = getattr(content_object, 'pk', getattr(content_object, 'id'))
        ))
        tree = []
        while len(comments) > 0:
            for i in xrange(len(comments)):
                if comments[i].parent == None:
                    comment = comments.pop(i)
                    setattr(comment, 'depth', 0)
                    tree.append(comment)
                    break
                elif comments[i].parent in tree:
                    comment = comments.pop(i)
                    idx = tree.index(comment.parent)
                    setattr(comment, 'depth', tree[idx].depth + 1)
                    tree.insert(idx + 1, comment)
                    break
                else:
                    continue
        return tree

class PublicThreadedCommentManager(ThreadedCommentManager):
    def get_query_set(self):
        return super(ThreadedCommentManager, self).get_query_set().filter(is_public = True)

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
    
    def get_content_object(self):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return self.content_type.get_object_for_this_type(pk=self.object_id)
        except ObjectDoesNotExist:
            return None
    
    public = PublicThreadedCommentManager()
    objects = ThreadedCommentManager()
    
    def __unicode__(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment[:50]
    
    def save(self):
        self.date_modified = datetime.now()
        super(ThreadedComment, self).save()
    
    class Meta:
        ordering = ('date_submitted',)

class Vote(models.Model):
    VOTE_CHOICES = (('+1', +1),('-1', -1))
    
    user = models.ForeignKey(User)
    comment = models.ForeignKey(ThreadedComment, related_name = 'votes')
    vote = models.IntegerField(choices=VOTE_CHOICES)