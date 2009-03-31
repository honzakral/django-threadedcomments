from django.test import TransactionTestCase, TestCase
from django.contrib import comments
from django.contrib.sites.models import Site
from django.template import loader
from django.conf import settings

from threadedcomments.util import annotate_tree_properties

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)

def sanitize_html(html):
    return '\n'.join(( i.strip() for i in html.split('\n') if i.strip() != '' ))

class SanityTests(TransactionTestCase):
    BASE_DATA = {
        'name': u'Eric Florenzano',
        'email': u'floguy@gmail.com',
        'comment': u'This is my favorite Django app ever!',
    }
    
    def _post_comment(self, data=None, parent=None):
        Comment = comments.get_model()
        body = (data or self.BASE_DATA).copy()
        url = comments.get_form_target()
        args = [Site.objects.all()[0]]
        kwargs = {}
        if parent is not None:
            kwargs['parent'] = unicode(parent.pk)
            body['parent'] = unicode(parent.pk)
        form = comments.get_form()(*args, **kwargs)
        body.update(form.generate_security_data())
        self.client.post(url, body, follow=True)
        return Comment.objects.order_by('-id')[0]
    
    def test_post_comment(self):
        Comment = comments.get_model()
        self.assertEqual(Comment.objects.count(), 0)
        comment = self._post_comment()
        self.assertEqual(comment.tree_path, str(comment.pk).zfill(PATH_DIGITS))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.last_child, None)
    
    def test_post_comment_child(self):
        comment = self._post_comment()
        self.assertEqual(comment.tree_path, str(comment.pk).zfill(PATH_DIGITS))
        child_comment = self._post_comment(parent=comment)
        comment_pk = str(comment.pk).zfill(PATH_DIGITS)
        child_comment_pk = str(child_comment.pk).zfill(PATH_DIGITS)
        self.assertEqual(child_comment.tree_path, PATH_SEPARATOR.join(
            (comment.tree_path, child_comment_pk)))
        self.assertEqual(comment.pk, child_comment.parent.pk)
        comment = comments.get_model().objects.get(pk=comment.pk)
        self.assertEqual(comment.last_child, child_comment)


class HierarchyTest(TransactionTestCase):
    fixtures = ['simple_tree']
    
    EXPECTED_HTML = sanitize_html('''
    <ul>
        <li>
            0000000001
            <ul>
                <li>
                    0000000001/0000000002
                    <ul>
                        <li>
                            0000000001/0000000002/0000000003
                        </li>
                        <li class="last">
                            0000000001/0000000002/0000000005
                        </li>
                    </ul>
                </li>
                <li class="last">
                    0000000001/0000000004
                    <ul>
                        <li class="last">
                            0000000001/0000000004/0000000006
                        </li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            0000000007
        </li>
    </ul>
    ''')

    def test_open_and_close_match(self):
        depth = 0
        for x in annotate_tree_properties(comments.get_model().objects.all()):
            depth += getattr(x, 'open', 0)
            self.assertEqual(x.depth, depth)
            depth -= len(getattr(x, 'close', []))

        self.assertEqual(0, depth)

    def test_last_flags_set_correctly_only_on_last_sibling(self):
        # construct the tree
        nodes = {}
        for x in comments.get_model().objects.all():
            nodes[x.pk] = (x, [])
            if x.parent_id:
                nodes[x.parent_id][1].append(x.pk)

        # check all the comments
        for x in annotate_tree_properties(comments.get_model().objects.all()):
            if getattr(x, 'last', False):
                # last comments have a parent
                self.assertTrue(x.parent_id)
                par, siblings = nodes[x.parent_id]

                # and ar last in their child list
                self.assertTrue( x.pk in siblings )
                self.assertEqual(len(siblings)-1, siblings.index(x.pk) )

    def test_template(self):
        output = loader.render_to_string('sample_tree.html')
        self.assertEqual(self.EXPECTED_HTML, sanitize_html(output))

    def test_last_child_properly_created(self):
        Comment = comments.get_model()
        new_child_comment = Comment(comment="Comment 8", site_id=1, content_type_id=7, object_pk=1, parent_id=1)
        new_child_comment.save()
        comment = Comment.objects.get(pk=1)
        self.assertEqual(comment.last_child, new_child_comment)

