from django.test import TransactionTestCase
from django.contrib import comments
from django.contrib.sites.models import Site

BASE_DATA = {
    'name': u'Eric Florenzano',
    'email': u'floguy@gmail.com',
    'comment': u'This is my favorite Django app ever!',
}

class SanityTests(TransactionTestCase):
    def _post_comment(self, base_data=BASE_DATA, parent=None):
        Comment = comments.get_model()
        data = base_data.copy()
        url = comments.get_form_target()
        args = [Site.objects.all()[0]]
        kwargs = {}
        if parent is not None:
            kwargs['parent'] = unicode(parent.pk)
            data['parent'] = unicode(parent.pk)
        form = comments.get_form()(*args, **kwargs)
        data.update(form.generate_security_data())
        self.client.post(url, data, follow=True)
        return Comment.objects.order_by('-id')[0]
    
    def test_post_comment(self):
        Comment = comments.get_model()
        self.assertEqual(Comment.objects.count(), 0)
        comment = self._post_comment()
        self.assertEqual(Comment.objects.count(), 1)
    
    def test_post_comment_child(self):
        comment = self._post_comment()
        child_comment = self._post_comment(parent=comment)
        self.assertEqual(comment.pk, child_comment.parent.pk)