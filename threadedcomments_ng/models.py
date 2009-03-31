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
                old.close = range(old.level - c.level)
                if old.root != c.root:
                    old.close.append(len(old.close))
                    last = []
                    c.open = 1
            yield old
            old = c
        old.close = range(old.level)
        yield old

    def pprint(self):
        """
        only proof of concepts, that it can be printed in template
        """
        t = '''
            {% for comment in comments.iter_tree %}
            {% if comment.open or comment.close %}
            </li>
            {% endif %}
            {% if comment.open %}
            <ul>
            % endif %}
            {% if comment.last %}
            <li class="last">
            {% else %}
            <li>
            {% endif %}
            {{ comment }}
            {% for close in comment.close %}
            </li>
            </ul>
            {% endfor %}
            {% endfor %}
        '''
        # render the template
        x = Template(t).render(Context({'comments': Comment.objects,}))
        # and print without empty lines
        print '\n'.join(( i.strip() for i in x.split('\n') if i.strip() != '' ))


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

