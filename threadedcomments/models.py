from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)
MAX_PATH_LENGTH = 255

class ThreadedComment(Comment):
    title = models.TextField(_('Title'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, default=None,
        related_name='children', verbose_name=_('Parent'))
    last_child = models.ForeignKey('self', null=True, blank=True,
        verbose_name=_('Last child'))
    tree_path = models.CharField(_('Tree path'), max_length=MAX_PATH_LENGTH, editable=False,
        db_index=True)

    objects = CommentManager()
    
    def _get_depth(self):
        return len(self.tree_path.split(PATH_SEPARATOR))
    depth = property(_get_depth)
    
    def _root_id(self):
        return self.tree_path.split(PATH_SEPARATOR)[0]
    root_id = property(_root_id)
    
    def save(self, *args, **kwargs):
        skip_tree_path = kwargs.pop('skip_tree_path', False)
        super(ThreadedComment, self).save(*args, **kwargs)
        if skip_tree_path:
            return None
        path_leaf = unicode(self.pk).zfill(PATH_DIGITS)
        if self.parent:
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, path_leaf))

            # XXX if tree_path is longer than fits into the DB field, make it reply
            # to it's grandparent. A hack for improbable situation
            while len(tree_path) > MAX_PATH_LENGTH:
                self.parent = self.parent.parent
                tree_path = PATH_SEPARATOR.join((self.parent.tree_path, path_leaf))

            self.parent.last_child = self
            ThreadedComment.objects.filter(pk=self.parent_id).update(
                last_child=self)
        else:
            tree_path = path_leaf

        self.tree_path = tree_path
        ThreadedComment.objects.filter(pk=self.pk).update(
            tree_path=self.tree_path)
    
    class Meta(object):
        ordering = ('tree_path',)
        db_table = 'threadedcomments_comment'
        verbose_name = _('Threaded comment')
        verbose_name_plural = _('Threaded comments')
