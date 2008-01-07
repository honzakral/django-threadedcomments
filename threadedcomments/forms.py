from django.contrib.auth.models import User
from django import newforms as forms
from models import ThreadedComment, Vote

class ThreadedCommentForm(forms.ModelForm):
    
    class Meta:
        model = ThreadedComment
        fields = ('comment',)