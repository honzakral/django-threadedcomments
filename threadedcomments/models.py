from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)

class ThreadedComment(Comment):
    title = models.TextField(_('Title'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name='children', verbose_name=_('Parent'))
    last_child = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Last child'))
    tree_path = models.TextField(_('Tree path'), editable=False, db_index=True)

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

    def save(self, *args, **kwargs):
        skip_tree_path = kwargs.pop('skip_tree_path', False)
        if skip_tree_path:
            super(ThreadedComment, self).save(*args, **kwargs)
            return None

        # Get pk
        c = Comment()
        d = {}
        for attr in c.__dict__.keys():
            d[attr] = self.__dict__[attr]

        del(d["_state"])
        c, created = Comment.objects.get_or_create(**d)	# save without sending signal
        self.id = self.pk = c.pk


        tree_path = unicode(self.pk).zfill(PATH_DIGITS)
        if self.parent:
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))

            d["id"] = c.id
            d["content_type_id"] = c.content_type_id
            ThreadedComment.objects.get_or_create(**d) # have to create, coz last_child_id cant be refere to anexist record
            self.parent.last_child = self
            ThreadedComment.objects.filter(pk=self.parent_id).update(last_child=self)


        self.tree_path = tree_path
        super(ThreadedComment, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # Fix last child on deletion.
        if self.parent_id:
            try:
                prev_child_id = ThreadedComment.objects \
                                .filter(parent=self.parent_id) \
                                .exclude(pk=self.pk) \
                                .order_by('-submit_date') \
                                .values_list('pk', flat=True)[0]
            except IndexError:
                prev_child_id = None
            ThreadedComment.objects.filter(pk=self.parent_id).update(last_child=prev_child_id)
        super(ThreadedComment, self).delete(*args, **kwargs)

    class Meta(object):
        ordering = ('tree_path',)
        db_table = 'threadedcomments_comment'
        verbose_name = _('Threaded comment')
        verbose_name_plural = _('Threaded comments')
