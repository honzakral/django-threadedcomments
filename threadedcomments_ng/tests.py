"""
really simple test for threadedcomments_ng

sorry it's only a doctest
"""

_html = '''
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
    <li class="last">
    0000000007
    </li>
</ul>
'''
# flat the html code
_html = '\n'.join(( i.strip() for i in _html.split('\n') if i.strip() != '' ))

test_html_output = r"""
>>> from threadedcomments_ng.models import Comment
>>> Comment.objects.pprint()
%s
""" % _html

__test__ = {
    "test_html_output": test_html_output,
}



from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

