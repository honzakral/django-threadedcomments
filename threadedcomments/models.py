from django.db import models
from django.contrib.comments.models import Comment
from django.conf import settings

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)


class ThreadedComment(Comment):
    parent = models.ForeignKey('self', null=True, blank=True, default=None,
        related_name='children')
    last_child = models.ForeignKey('self', null=True, blank=True)
    tree_path = models.CharField(max_length=255, editable=False, db_index=True)
    
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
        tree_path = unicode(self.pk).zfill(PATH_DIGITS)
        if self.parent:
            self.parent.last_child = self
            ThreadedComment.objects.filter(pk=self.parent_id).update(
                last_child=self)
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))

        self.tree_path = tree_path
        ThreadedComment.objects.filter(pk=self.pk).update(
            tree_path=self.tree_path)
    
    class Meta(object):
        ordering = ('tree_path',)
        db_table = 'threadedcomments_comment'
