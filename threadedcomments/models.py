from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from datetime import datetime

MARKDOWN = 1
TEXTILE = 2
REST = 3
HTML = 4
PLAINTEXT = 5
MARKUP_CHOICES = (
    (MARKDOWN, "markdown"),
    (TEXTILE, "textile"),
    (REST, "restructuredtext"),
    (HTML, "html"),
    (PLAINTEXT, "plaintext"),
)

def dfs(node, todo):
    node.depth = 0
    to_return = [node,]
    for n in todo:
        if n.parent is not None and n.parent.id == node.id:
            todo.remove(n)
            for subnode in dfs(n, todo):
                subnode.depth = subnode.depth + 1
                to_return.append(subnode)
    return to_return

class ThreadedCommentManager(models.Manager):
    def get_tree(self, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        children = list(self.get_query_set().filter(
            content_type = content_type,
            object_id = getattr(content_object, 'pk', getattr(content_object, 'id')),
        ).select_related())
        to_return = []
        for child in children:
            to_return.extend(dfs(child, children))
        return to_return

    def _generate_object_kwarg_dict(self, content_object, **kwargs):
        kwargs['content_type'] = ContentType.objects.get_for_model(content_object)
        kwargs['object_id'] = getattr(content_object, 'pk', getattr(content_object, 'id'))
        return kwargs

    def create_for_object(self, content_object, **kwargs):
        return self.create(**self._generate_object_kwarg_dict(content_object, **kwargs))
    
    def get_or_create_for_object(self, content_object, **kwargs):
        return self.get_or_create(**self._generate_object_kwarg_dict(content_object, **kwargs))
    
    def get_for_object(self, content_object, **kwargs):
        return self.get(**self._generate_object_kwarg_dict(content_object, **kwargs))

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
    markup = models.IntegerField(choices=MARKUP_CHOICES, default=PLAINTEXT)
    is_public = models.BooleanField(default = True)
    is_approved = models.BooleanField(default = True)
    ip_address = models.IPAddressField(null=True, blank=True)
    
    def _get_score(self):
        score = 0
        for vote in self.votes.all():
            score = score + vote.vote
        return score
    score = property(_get_score)
    
    def get_content_object(self):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return self.content_type.get_object_for_this_type(pk = self.object_id)
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
    
    def get_base_data(self, show_dates=True):
        markup = "plaintext"
        for markup_choice in MARKUP_CHOICES:
            if self.markup == markup_choice[0]:
                markup = markup_choice[1]
                break
        to_return = {
            'content_object' : self.get_content_object(),
            'parent' : self.parent,
            'user' : self.user,
            'comment' : self.comment,
            'is_public' : self.is_public,
            'is_approved' : self.is_approved,
            'ip_address' : self.ip_address,
            'markup' : markup,
        }
        if show_dates:
            to_return['date_submitted'] = self.date_submitted
            to_return['date_modified'] = self.date_modified
            to_return['date_approved'] = self.date_approved
        return to_return
    
    class Meta:
        ordering = ('date_submitted',)
        verbose_name = "Threaded Comment"
        verbose_name_plural = "Threaded Comments"
        get_latest_by = "date_submitted"
    
    class Admin:
        fields = (
            (None, {'fields': ('content_type', 'object_id')}),
            ('Parent', {'fields' : ('parent',)}),
            ('Content', {'fields': ('user', 'comment')}),
            ('Meta', {'fields': ('is_public', 'date_submitted', 'date_modified', 'date_approved', 'is_approved', 'ip_address')}),
        )
        list_display = ('user', 'date_submitted', 'content_type', 'get_content_object', 'parent', 'score')
        list_filter = ('date_submitted',)
        date_hierarchy = 'date_submitted'
        search_fields = ('comment', 'user__username')

class FreeThreadedComment(models.Model):
    # Generic Foreign Key Stuff
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    # Hierarchy Stuff
    parent = models.ForeignKey('self', null = True, default = None, related_name='children')
    
    # User-Replacement Stuff
    name = models.CharField(max_length = 128)
    website = models.URLField(blank = True)
    email = models.EmailField(blank = True)
    
    # Meat n' Potatoes
    date_submitted = models.DateTimeField(default = datetime.now)
    date_modified = models.DateTimeField(default = datetime.now)
    date_approved = models.DateTimeField(default = datetime.now)
    comment = models.TextField()
    markup = models.IntegerField(choices=MARKUP_CHOICES, default=PLAINTEXT)
    
    is_public = models.BooleanField(default = True)
    is_approved = models.BooleanField(default = True)
    ip_address = models.IPAddressField(null=True, blank=True)
    
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
        super(FreeThreadedComment, self).save()
    
    def get_base_data(self, show_dates=True):
        markup = "plaintext"
        for markup_choice in MARKUP_CHOICES:
            if self.markup == markup_choice[0]:
                markup = markup_choice[1]
                break
        to_return = {
            'content_object' : self.get_content_object(),
            'parent' : self.parent,
            'name' : self.name,
            'website' : self.website,
            'email' : self.email,
            'comment' : self.comment,
            'is_public' : self.is_public,
            'is_approved' : self.is_approved,
            'ip_address' : self.ip_address,
            'markup' : markup,
        }
        if show_dates:
            to_return['date_submitted'] = self.date_submitted
            to_return['date_modified'] = self.date_modified
            to_return['date_approved'] = self.date_approved
        return to_return
    
    class Meta:
        ordering = ('date_submitted',)
        verbose_name = "Free Threaded Comment"
        verbose_name_plural = "Free Threaded Comments"
        get_latest_by = "date_submitted"
    
    class Admin:
        fields = (
            (None, {'fields': ('content_type', 'object_id')}),
            ('Parent', {'fields' : ('parent',)}),
            ('Content', {'fields': ('name', 'website', 'email', 'comment')}),
            ('Meta', {'fields': ('date_submitted', 'date_modified', 'date_approved', 'is_public', 'ip_address', 'is_approved')}),
        )
        list_display = ('name', 'date_submitted', 'content_type', 'get_content_object', 'parent', 'score')
        list_filter = ('date_submitted',)
        date_hierarchy = 'date_submitted'
        search_fields = ('comment', 'name', 'email', 'website')

class TestModel(models.Model):
    """
    This model is simply used by this application's test suite as a model to 
    which to attach comments.
    """
    name = models.CharField(max_length=5)
    is_public = models.BooleanField(default=True)
    date = models.DateTimeField(default=datetime.now)