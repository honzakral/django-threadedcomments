"""
Change the attributes you want to customize
"""
from threadedcomments.models import ThreadedComment
from threadedcomments.forms import ThreadedCommentForm

# following PEP 386
__version__ = "0.9.0"

def get_model():
    return ThreadedComment

def get_form():
    return ThreadedCommentForm
