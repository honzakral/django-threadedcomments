"""
Change the attributes you want to customize
"""

from threadedcomments.models import ThreadedComment
from threadedcomments.forms import ThreadedCommentForm

def get_model():
    return ThreadedComment

def get_form():
    return ThreadedCommentForm
