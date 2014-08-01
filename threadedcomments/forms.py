from django import forms
from django.contrib.comments.forms import CommentForm
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from threadedcomments.models import ThreadedComment

class ThreadedCommentForm(CommentForm):
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def insert_title(self):
        new_base_fields = SortedDict()
        for key, value in self.base_fields.items():
            if key == 'comment':
                new_base_fields['title'] = forms.CharField(label=_('Title'), required=False, max_length=getattr(settings, 'COMMENTS_TITLE_MAX_LENGTH', 255))
            new_base_fields[key] = value
        self.base_fields = new_base_fields

    def __init__(self, target_object, parent=None, data=None, initial=None):
        self.insert_title()

        self.parent = parent
        if initial is None:
            initial = {}
        initial.update({'parent': self.parent})
        super(ThreadedCommentForm, self).__init__(target_object, data=data, initial=initial)

    def get_comment_model(self):
        return ThreadedComment

    def get_comment_create_data(self):
        d = super(ThreadedCommentForm, self).get_comment_create_data()
        d['parent_id'] = self.cleaned_data['parent']
        d['title'] = self.cleaned_data['title']
        return d

