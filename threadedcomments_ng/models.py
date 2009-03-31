from django.db import models
from django.template import Template, Context


DIGITS = 10
SEPARATOR = '/'


class CommentManager(models.Manager):
    def iter_tree(self):
        """
        iterate through nodes and adds some magic properties to each of them
        representing opening list of children and closing it
        """
        it = self.all().iterator()

        # get the first item, this will fail if no items !
        old = it.next()

        # first item starts a new thread
        old.open = 1
        last = set()
        for c in it:
            # if this comment has a parent, store it's last child for future reference
            if old.last_child_id:
                last.add(old.last_child_id)

            # this is the last child, mark it
            if c.pk in last:
                c.last = True

            # increase the level
            if c.level > old.level:
                c.open = 1

            else: # c.level <= old.level
                # close some levels
                old.close = range(old.level - c.level)

                # new thread
                if old.root != c.root:
                    # close even the top level
                    old.close.append(len(old.close))
                    # and start a new thread
                    c.open = 1
                    # empty the last set
                    last = set()
            # iterate
            yield old
            old = c

        old.close = range(old.level)
        yield old

class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child_set')
    last_child = models.ForeignKey('self', null=True, blank=True)
    tree_path = models.TextField(editable=False)

    objects = CommentManager()

    def __unicode__(self):
        return self.tree_path

    class Meta:
        ordering = ('tree_path',)

    @property
    def level(self):
        return len(self.tree_path.split(SEPARATOR))

    @property
    def root(self):
        return self.tree_path.split(SEPARATOR)[0]

    def save(self, force_update=False, force_insert=False):
        super(Comment, self).save(force_update=force_update, force_insert=force_insert)

        tp = ''
        if self.parent:
            tp = self.parent.tree_path + SEPARATOR
            self.parent.last_child = self
            self.__class__.objects.filter(pk=self.parent_id).update(last_child=self)
            
        tree_path = tp + '%%0%dd' % DIGITS % self.pk
        self.tree_path = tree_path
        self.__class__.objects.filter(pk=self.pk).update(tree_path=tree_path)

