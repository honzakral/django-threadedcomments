"""
Change the attributes you want to customize
"""


# following PEP 440
__version__ = "1.0.1"

def get_model():
    from threadedcomments.models import ThreadedComment
    return ThreadedComment

def get_form():
    from threadedcomments.forms import ThreadedCommentForm
    return ThreadedCommentForm
