from django.test import TestCase
from django.template import loader

from threadedcomments_ng.models import Comment

class SimpleTest(TestCase):
    fixtures = ['simple_tree']

    def test_open_and_close_match(self):
        level = 0
        for x in Comment.objects.iter_tree():
            level += getattr(x, 'open', 0)
            self.assertEqual(x.level, level)
            level -= len(getattr(x, 'close', []))

        self.assertEqual(0, level)

    def test_last_flags_set_correctly_only_on_last_sibling(self):
        # construct the tree
        nodes = {}
        for x in Comment.objects.all():
            nodes[x.pk] = (x, [])
            if x.parent_id:
                nodes[x.parent_id][1].append(x.pk)

        # check all the cmments
        for x in Comment.objects.iter_tree():
            if getattr(x, 'last', False):
                # last comments have a parent
                self.assertTrue(x.parent_id)
                par, siblings = nodes[x.parent_id]

                # and ar last in their child list
                self.assertTrue( x.pk in siblings )
                self.assertEqual(len(siblings)-1, siblings.index(x.pk) )

    def test_template(self):
        output = loader.render_to_string('sample_tree.html', {'comment_list': Comment.objects.iter_tree() })

        
        self.assertEqual(expected_html, sanitize_html(output))

def sanitize_html(html):
    return '\n'.join(( i.strip() for i in html.split('\n') if i.strip() != '' ))
expected_html = sanitize_html('''
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
