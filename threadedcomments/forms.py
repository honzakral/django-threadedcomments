from django.contrib.auth.models import User
from django import newforms as forms
from models import FreeThreadedComment, ThreadedComment

class ThreadedCommentForm(forms.ModelForm):
    
    class Meta:
        model = ThreadedComment
        fields = ('comment',)

class FreeThreadedCommentForm(forms.ModelForm):
    
    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'name', 'website', 'email')