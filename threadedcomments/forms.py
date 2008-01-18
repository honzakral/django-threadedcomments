from django.contrib.auth.models import User
from django import newforms as forms
from models import FreeThreadedComment, ThreadedComment

class ThreadedCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new ThreadedComment.
    It consists of just one field: Comment.  I'm not e
    """
    class Meta:
        model = ThreadedComment
        fields = ('comment', 'markup')

class FreeThreadedCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new FreeThreadedComment.
    """
    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email', 'markup')