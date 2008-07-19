import datetime
from django.dispatch import dispatcher
from django.db.models import signals
from models import ThreadedComment, FreeThreadedComment, MARKUP_CHOICES
from models import DEFAULT_MAX_COMMENT_LENGTH, DEFAULT_MAX_COMMENT_DEPTH
from comment_utils import moderation

MARKUP_CHOICES_IDS = [c[0] for c in MARKUP_CHOICES]


class CommentModerator(moderation.CommentModerator):
    max_comment_length = DEFAULT_MAX_COMMENT_LENGTH
    allowed_markup = MARKUP_CHOICES_IDS
    max_depth = DEFAULT_MAX_COMMENT_DEPTH

    def _is_past_max_depth(self, comment):
        i = 1
        c = comment.parent
        while c != None:
            c = c.parent
            i = i + 1
            if i > self.max_depth:
                return True
        return False

    def allow(self, comment, content_object):
        if self._is_past_max_depth(comment):
            return False
        if comment.markup not in self.allowed_markup:
            return False
        return super(CommentModerator, self).allow(comment, content_object)

    def moderate(self, comment, content_object):
        if len(comment.comment) > self.max_comment_length:
            return True
        return super(CommentModerator, self).moderate(comment, content_object)

class Moderator(moderation.Moderator):
    def connect(self):
        for model in (ThreadedComment, FreeThreadedComment):
            dispatcher.connect(self.pre_save_moderation, sender=model, signal=signals.pre_save)
            dispatcher.connect(self.post_save_moderation, sender=model, signal=signals.post_save)
    
# Instantiate the ``ThreadedModerator`` so that other modules can import and 
# begin to register with it.

moderator = Moderator()