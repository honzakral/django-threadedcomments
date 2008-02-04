import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, loader
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.dispatch import dispatcher
from django.db.models import signals
from django.db.models.base import ModelBase
from models import ThreadedComment, FreeThreadedComment, MARKUP_CHOICES

MARKUP_CHOICES_IDS = [c[0] for c in MARKUP_CHOICES]
DEFAULT_MAX_COMMENT_LENGTH = getattr(settings, 'DEFAULT_MAX_COMMENT_LENGTH', 1000)
DEFAULT_MAX_COMMENT_DEPTH = getattr(settings, 'DEFAULT_MAX_COMMENT_DEPTH', 8)

class ThreadedCommentManager(object):
    """
    Basic moderation (configuration) object which is to be stored in the registry.
    This also provides compatibility with comment_utils_.
    
    .. _comment_utils: http://code.google.com/p/django-comment-utils/
    """
    akismet = None
    auto_close_field = None
    close_after = None
    enable_field = None
    email_notification = None
    max_comment_length = None
    allowed_markup = None
    max_depth = None

class Moderator(object):
    """
    A ``Moderator`` provides functionality for determining whether a comment should be
    immediately deleted or disallowed by the recommendation of an external service.
     
    More technically, it provides model to moderation-options registration and 
    unregistration.  It also provides for pre_save and post_save signal handlers.
    """
    def __init__(self):
        self._registry = {}

    def register(self, model, manager = None, akismet = None, 
        auto_close_field = None, close_after = None, enable_field = None,
        email_notification = None, max_comment_length = DEFAULT_MAX_COMMENT_LENGTH,
        allowed_markup = MARKUP_CHOICES_IDS, max_depth=DEFAULT_MAX_COMMENT_DEPTH):
        """
        Registers a model with a set of moderation options in one of two ways:

        1. Passing in a ``ThreadedCommentManager`` class under the ``manager``
           keyword argument.  This class may also be a subclass of a manager
           provided by the excellent comment_utils_.

           If this option is chosen, all other keyword arguments will be ignored.

        2. Passing in one or more of the following keyword arguments:
           :akismet:
               *True* or *False*, determines whether **akismet** is used to filter
               spam from real comments.

           .. _auto_close_field:
           :auto_close_field:
               A string representation of a ``DateField`` or a ``DateTimeField``
               to be used in conjunction with close_after_.

           .. _close_after:
           :close_after:
               An integer describing the number of days after an auto_close_field_
               to disallow any further comments.

           :enable_field:
               A string representation of a ``BooleanField`` on the related model
               which, when set to *False*, will disallow any further comments.

           :email_notification:
               *True* or *False*, dictates whether to send administrators an
               email upon a successfully saved new comment.
        
           :max_comment_length:
               An integer representing the maximum length (in characters) that the
               comment may be.  Defaults to 1000.
            
           :allowed_markup:
               A list of integers derived from ``MARKUP_CHOICES`` in the models
               file.  If a comment is submitted on an object with a different
               markup than is allowed, then it will be immediately deleted.

            :max_depth:
               The maximum "depth" of a comment.  That is, it will take no
               more than max_depth parent relationship traversals to hit a
               comment with no parent.

        .. _comment_utils: http://code.google.com/p/django-comment-utils/
        """
        if manager:
            moderation_obj = ThreadedCommentManager()
            moderation_obj.akismet = manager.akismet
            moderation_obj.auto_close_field = manager.auto_close_field
            moderation_obj.close_after = manager.close_after
            moderation_obj.enable_field = manager.enable_field
            moderation_obj.email_notification = manager.email_notification
            moderation_obj.max_comment_length = getattr(manager, 'max_comment_length', max_comment_length)
            moderation_obj.allowed_markup = getattr(manager, 'allowed_markup', allowed_markup)
            moderation_obj.max_depth = getattr(manager, 'max_depth', max_depth)
            self._registry[model] = moderation_obj
        else:
            if close_after:
                assert auto_close_field is not None
            moderation_obj = ThreadedCommentManager()
            moderation_obj.akismet = akismet
            moderation_obj.auto_close_field = auto_close_field
            moderation_obj.close_after = close_after
            moderation_obj.enable_field = enable_field
            moderation_obj.email_notification = email_notification
            moderation_obj.max_comment_length = max_comment_length
            moderation_obj.allowed_markup = allowed_markup
            moderation_obj.max_depth = max_depth
            self._registry[model] = moderation_obj
        for klass in (ThreadedComment, FreeThreadedComment):
            dispatcher.connect(self.pre_save, sender=klass, signal=signals.pre_save)
            dispatcher.connect(self.post_save, sender=klass, signal=signals.post_save)

    def unregister(self, model):
        """
        Given a model class, unregisters any moderation options for that class.
        """
        del self._registry[model]

    def is_spam(self, comment):
        """
        Checks **akismet** to see whether a given ``comment`` object is thought to be spam.
        """
        from akismet import Akismet
        from django.utils.encoding import smart_str
        akismet_api = Akismet(key=settings.AKISMET_API_KEY,
                                blog_url='http://%s/' % Site.objects.get_current().domain)
        if akismet_api.verify_key():
            akismet_data = { 'comment_type': 'comment',
                                'referrer': '',
                                'user_ip': comment.ip_address,
                                'user_agent': '' }
            if akismet_api.comment_check(smart_str(comment.comment), data=akismet_data, build_data=True):
                return True
        else:
            assert False, "Akismet must be installed with a valid API Key"
        return False

    def is_disabled(self, content_object, enable_field):
        """
        Checks to see whether the ``enable_field`` is set to *False*.
        """
        if getattr(content_object, enable_field):
            return False
        return True

    def is_closed(self, content_object, auto_close_field, close_after):
        """
        Determines whether a comment is past the date where it is considered open.
        
        If the ``content_object``'s ``auto_close_field`` is ``close_after`` days
        earlier than today, then this returns *True*.  Otherwise, it returns *False*.
        """
        if datetime.datetime.now() - datetime.timedelta(days=close_after) > getattr(content_object, auto_close_field):
            return True
        return False

    def is_past_max_depth(self, comment, max_depth):
        i = 1
        c = comment.parent
        while c != None:
            c = c.parent
            i = i + 1
            if i > max_depth:
                return True
        return False

    def do_emails(self, comment):
        """
        Renders and sends e-mails to all administrators listed in the settings.
        """
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        t = loader.get_template('threadedcomments/comment_notification_email.txt')
        c = Context({ 'comment': comment })
        subject = '[%s] New comment posted on "%s"' % (Site.objects.get_current().name,
                                                          comment.content_object)
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

    def annotate_deletion(self, comment):
        """
        Flags a comment for ``post_save`` deletion.
        """
        comment.moderation_disallowed = True
    
    def has_annotation(self, comment):
        """
        Checks whether a comment has been flagged for ``post_save`` deletion.
        """
        if hasattr(comment, 'moderation_disallowed'):
            return True
        return False

    def pre_save(self, sender, instance):
        """
        Handles signals emitted by comment objects before being saved.  Mainly, this
        means that it checks to see whether a comment should be flagged for deletion,
        set to ``is_public``=*False*, or left unmoderated.
        """
        model = instance.content_type.model_class()
        if model not in self._registry:
            return
        c = self._registry[model]
        # c is the moderation object or moderation configuration, named c for conciseness
        if c.akismet and self.is_spam(instance):
            instance.is_public = False
        if len(instance.comment) > c.max_comment_length:
            instance.is_public = False
        if self.is_past_max_depth(instance, c.max_depth):
            instance.is_public = False
        if instance.markup not in c.allowed_markup:
            self.annotate_deletion(instance)
            return
        if c.enable_field and self.is_disabled(instance.content_object, c.enable_field):
            self.annotate_deletion(instance)
            return
        if c.auto_close_field and c.close_after and self.is_closed(instance.content_object, c.auto_close_field, c.close_after):
            self.annotate_deletion(instance)
            return
        return
    
    def post_save(self, sender, instance):
        """
        Handles signals emitted by comment objects after being saved.  Mainly, this
        means that it deletes comments or does e-mails upon successful comment save.
        """
        model = instance.content_type.model_class()
        if model not in self._registry:
            return
        if self.has_annotation(instance):
            instance.delete()
            return
        if self._registry[model].email_notification:
            self.do_emails(instance)

# Instantiate the ``Moderator`` so that other modules can import and begin to register
# with it.
moderator = Moderator()