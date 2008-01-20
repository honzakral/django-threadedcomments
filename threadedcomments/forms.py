from django.contrib.auth.models import User
from django import newforms as forms
from models import FreeThreadedComment, ThreadedComment
from django.conf import settings

MAX_COMMENT_LENGTH = getattr(settings, 'MAX_COMMENT_LENGTH', 1000)

class ThreadedCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new ThreadedComment.
    It consists of just two fields: ``comment``, and ``markup``.
    
    The ``comment`` field is the only one which is required.
    """
    comment = forms.CharField(max_length=MAX_COMMENT_LENGTH, widget=forms.widgets.Textarea)
    class Meta:
        model = ThreadedComment
        fields = ('comment', 'markup')

class FreeThreadedCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new FreeThreadedComment.
    It consists of just a few fields: ``comment``, ``name``, ``website``,
    ``email``, and ``markup``.
    
    The fields ``comment``, and ``name`` are the only ones which are required.
    """
    comment = forms.CharField(max_length=MAX_COMMENT_LENGTH, widget=forms.widgets.Textarea)
    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email', 'markup')