import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, loader
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.dispatch import dispatcher
from django.db.models import signals
from django.db.models.base import ModelBase
from models import ThreadedComment, FreeThreadedComment

AKISMET_DEFAULT = getattr(settings, 'AKISMET_DEFAULT_ON', False)

class ThreadedCommentManager(object):
    akismet = None
    auto_close_field = None
    close_after = None
    enable_field = None
    email_notification = None

class Moderator(object):
    def __init__(self):
        self._registry = {}

    def register(self, model, manager=None, akismet=AKISMET_DEFAULT, auto_close_field = None,
        close_after = None, enable_field = None, email_notification = None):
        if manager:
            self._registry[model] = manager
        else:
            if close_after:
                assert auto_close_field is not None
            moderation_obj = ThreadedCommentManager()
            moderation_obj.akismet = akismet
            moderation_obj.auto_close_field = auto_close_field
            moderation_obj.close_after = close_after
            moderation_obj.enable_field = enable_field
            moderation_obj.email_notification = email_notification
            self._registry[model] = moderation_obj
        for klass in (ThreadedComment, FreeThreadedComment):
            dispatcher.connect(self.pre_save, sender=klass, signal=signals.pre_save)
            dispatcher.connect(self.post_save, sender=klass, signal=signals.post_save)

    def unregister(self, model):
        del self._registry[model]

    def is_spam(self, comment):
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
        if getattr(content_object, enable_field):
            return False
        return True

    def is_closed(self, content_object, auto_close_field, close_after):
        if datetime.datetime.now() - datetime.timedelta(days=close_after) > getattr(content_object, auto_close_field):
            return True
        return False

    def do_emails(self, comment):
        content_object = comment.get_content_object()
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        t = loader.get_template('threadedcomments/comment_notification_email.txt')
        c = Context({ 'comment': comment,
                      'content_object': content_object })
        subject = '[%s] New comment posted on "%s"' % (Site.objects.get_current().name,
                                                          content_object)
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

    def annotate_deletion(self, comment):
        comment.moderation_disallowed = True
    
    def has_annotation(self, comment):
        if hasattr(comment, 'moderation_disallowed'):
            return True
        return False

    def pre_save(self, sender, instance):
        model = instance.content_type.model_class()
        if model not in self._registry:
            return
        content_object = instance.get_content_object()
        c = self._registry[model]
        # c is the moderation object or moderation configuration, named c for conciseness
        if c.akismet and self.is_spam(instance):
            instance.is_public = False
        if c.enable_field and self.is_disabled(content_object, c.enable_field):
            self.annotate_deletion(instance)
            return
        if c.auto_close_field and c.close_after and self.is_closed(content_object, c.auto_close_field, c.close_after):
            self.annotate_deletion(instance)
            return
        return
    
    def post_save(self, sender, instance):
        model = instance.content_type.model_class()
        if model not in self._registry:
            return
        if self.has_annotation(instance):
            instance.delete()
            return
        if self._registry[model].email_notification:
            self.do_emails(instance)

moderator = Moderator()