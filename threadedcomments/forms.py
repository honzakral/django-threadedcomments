from django import forms
from django.contrib.comments.forms import CommentForm
from django.conf import settings
from django.utils.hashcompat import sha_constructor

from threadedcomments.models import ThreadedComment

class ThreadedCommentForm(CommentForm):
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, target_object, parent=None, data=None, initial=None):
        self.parent = parent
        if initial is None:
            initial = {}
        initial.update({'parent': self.parent})
        super(ThreadedCommentForm, self).__init__(target_object, data=data,
            initial=initial)

    def get_comment_object(self):
        new_comment = super(ThreadedCommentForm, self).get_comment_object()
        new_threaded_comment = ThreadedComment(
            content_type=new_comment.content_type,
            object_pk=new_comment.object_pk,
            user_name=new_comment.user_name,
            user_email=new_comment.user_email,
            user_url=new_comment.user_url,
            comment=new_comment.comment,
            submit_date=new_comment.submit_date,
            site_id=new_comment.site_id,
            is_public=new_comment.is_public,
            is_removed=new_comment.is_removed,
            parent_id=self.cleaned_data['parent']
        )
        return new_threaded_comment

    def clean_security_hash(self):
        """
        Check the security hash.
        """
        security_hash_dict = {
            'content_type': self.data.get('content_type', ''),
            'object_pk': self.data.get('object_pk', ''),
            'timestamp': self.data.get('timestamp', ''),
            'parent': self.data.get('parent', '')
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data['security_hash']
        if expected_hash != actual_hash:
            raise forms.ValidationError('Security hash check failed.')
        return actual_hash

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """
        initial_security_dict = {
            'content_type': str(self.target_object._meta),
            'object_pk': str(self.target_object._get_pk_val()),
            'timestamp': str(timestamp),
            'parent': str(self.parent or ''),
        }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, timestamp, parent):
        """
        Generate a (SHA1) security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp, parent, settings.SECRET_KEY)
        return sha_constructor(''.join(info)).hexdigest()
