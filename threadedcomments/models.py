from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from .compat import Comment, CommentManager

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)


class ThreadedComment(Comment):
    title = models.TextField(_('Title'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name='children', verbose_name=_('Parent'))
    last_child = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Last child'))
    tree_path = models.CharField(_('Tree path'), max_length=500, editable=False)
    newest_activity = models.DateTimeField(null=True)

    objects = CommentManager()

    @property
    def depth(self):
        return len(self.tree_path.split(PATH_SEPARATOR))

    @property
    def root_id(self):
        return int(self.tree_path.split(PATH_SEPARATOR)[0])

    @property
    def root_path(self):
        return ThreadedComment.objects.filter(pk__in=self.tree_path.split(PATH_SEPARATOR)[:-1])

    @transaction.atomic
    def save(self, *args, **kwargs):
        skip_tree_path = kwargs.pop('skip_tree_path', False)
        super(ThreadedComment, self).save(*args, **kwargs)
        if skip_tree_path:
            return None

        tree_path = str(self.pk).zfill(PATH_DIGITS)
        if self.parent:
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))

            self.parent.last_child = self
            ThreadedComment.objects.filter(pk=self.parent_id).update(last_child=self.id)
            ThreadedComment.objects.filter(pk=self.parent_id).update(newest_activity=self.submit_date)
            ThreadedComment.objects.filter(parent_id=self.parent_id).update(newest_activity=self.submit_date)

        self.tree_path = tree_path
        ThreadedComment.objects.filter(pk=self.pk).update(tree_path=self.tree_path)
        ThreadedComment.objects.filter(pk=self.pk).update(newest_activity=self.submit_date)

    def delete(self, *args, **kwargs):
        # Fix last child on deletion.
        if self.parent_id:
            try:
                prev_child = ThreadedComment.objects \
                    .filter(parent=self.parent_id) \
                    .exclude(pk=self.pk) \
                    .order_by('-submit_date')[0]
            except IndexError:
                prev_child = None
            if prev_child:
                ThreadedComment.objects.filter(pk=self.parent_id).update(last_child=prev_child)
                ThreadedComment.objects.filter(pk=self.parent_id).update(newest_activity=prev_child.submit_date)
                ThreadedComment.objects.filter(parent_id=self.parent_id).update(newest_activity=prev_child.submit_date)
            else:
                ThreadedComment.objects.filter(pk=self.parent_id).update(last_child=None)
                ThreadedComment.objects.filter(pk=self.parent_id).update(newest_activity=self.parent.submit_date)

        super(ThreadedComment, self).delete(*args, **kwargs)

    class Meta(object):
        ordering = ('tree_path',)
        db_table = 'threadedcomments_comment'
        verbose_name = _('Threaded comment')
        verbose_name_plural = _('Threaded comments')
