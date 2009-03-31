from django.db import models

DIGITS = 10
SEPARATOR = '/'


class CommentManager(models.Manager):
    def iter_tree(self):
        """
        iterate through nodes and adds some magic properties to each of them
        representing opening list of children and closing it
        """
        it = self.all().iterator()

        old = it.next()
        old.open = 1
        last = []
        for c in it:
            if old.last_child_id:
                last.append(old.last_child_id)

            if c.pk in last:
                c.last = True

            if c.level > old.level:
                c.open = 1

            else: # c.level <= old.level
                old.close = old.level - c.level
                if old.root != c.root:
                    old.close += 1
                    last = []
                    c.open = 1
            yield old
            old = c
        old.close = old.level
        yield old

    def pprint(self):
        for c in self.iter_tree():
            if not  getattr(c, 'open', False) and not getattr(c, 'close', False):
                print '</li>'

            if getattr(c, 'open', False):
                print '<ul>'

            if getattr(c, 'last', False):
                print '<li class="last">'
            else:
                print '<li>'

            print '%s' % c

            for x in range(getattr(c, 'close', 0)):
                print '</li>'
                print '</ul>'



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

