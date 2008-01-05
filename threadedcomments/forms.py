from django.contrib.auth.models import User
from django import newforms as forms
from models import ThreadedComment, Vote

class ThreadedCommentForm(forms.ModelForm):
    content_type = forms.IntegerField(widget = forms.HiddenInput)
    object_id = forms.IntegerField(widget = forms.HiddenInput)
    parent = forms.ModelChoiceField(ThreadedComment.objects.all(), required=False, widget = forms.HiddenInput)
    user = forms.ModelChoiceField(User.objects.all(), widget = forms.HiddenInput)
    next = forms.CharField(required=False)
    
    class Meta:
        model = ThreadedComment
        fields = ('content_type', 'object_id', 'parent', 'comment', 'user')

class VoteForm(forms.ModelForm):
    comment = forms.ModelChoiceField(ThreadedComment.objects.all(), widget = forms.HiddenInput)
    vote = forms.ChoiceField(choices=Vote.VOTE_CHOICES)
    user = forms.ModelChoiceField(User.objects.all(), widget = forms.HiddenInput)
    next = forms.CharField(required=False)
    
    class Meta:
        model = Vote