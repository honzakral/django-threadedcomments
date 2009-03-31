from django.test import TransactionTestCase
from django.contrib import comments
from django.contrib.sites.models import Site

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
        self.assertEqual(comment.tree_path, '0000000001')
        self.assertEqual(Comment.objects.count(), 1)
    
    def test_post_comment_child(self):
        comment = self._post_comment()
        self.assertEqual(comment.tree_path, '0000000001')
        child_comment = self._post_comment(parent=comment)
        self.assertEqual(child_comment.tree_path, '0000000002/0000000001')
        self.assertEqual(comment.pk, child_comment.parent.pk)