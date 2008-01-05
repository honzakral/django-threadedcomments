import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, loader
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.dispatch import dispatcher
from django.db.models import signals
from django.db.models.base import ModelBase
from models import ThreadedComment

class ThreadedCommentModerator(object):
    akismet = getattr(settings, 'AKISMET_DEFAULT_ON', False)
    auto_close_field = None
    close_after = None
    enable_field = None
    email_notification = None

    def __init__(self, model):
        self._model = model

    def allow(self, comment, comment_object):
        if self.enable_field:
            if getattr(content_object, self.enable_field) == False:
                return False
        if self.auto_close_field and self.close_after:
            if datetime.datetime.now() - datetime.timedelta(days=self.close_after) > getattr(content_object, self.auto_close_field):
                return False
        return True

    def moderate(self, comment, content_object):
        if self.akismet:
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
        return False

    def email(self, comment, content_object):
        if not self.email_notification:
            return
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        t = loader.get_template('threadedcomments/comment_notification_email.txt')
        c = Context({ 'comment': comment,
                      'content_object': content_object })
        subject = '[%s] New comment posted on "%s"' % (Site.objects.get_current().name,
                                                          content_object)
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

class Moderator(object):
    def __init__(self):
        self._registry = {}
        dispatcher.connect(self.pre_save_moderation, sender=ThreadedComment, signal=signals.pre_save)
        dispatcher.connect(self.post_save_moderation, sender=ThreadedComment, signal=signals.post_save)
    
    def register(self, model_or_iterable, moderation_class):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = (model_or_iterable,)
        for model in model_or_iterable:
            self._registry[model] = moderation_class(model)
    
    def unregister(self, model_or_iterable):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = (model_or_iterable,)
        for model in model_or_iterable:
            del self._registry[model]
    
    def pre_save_moderation(self, sender, instance):
        model = instance.content_type.model_class()
        if instance.id or (model not in self._registry):
            return
        content_object = instance.get_content_object()
        moderation_class = self._registry[model]
        if not moderation_class.allow(instance, content_object): # Comment will get deleted in post-save hook.
            instance.__moderation_disallowed = True
            return
        if moderation_class.moderate(instance, content_object):
            instance.is_public = False
    
    def post_save_moderation(self, sender, instance):
        model = instance.content_type.model_class()
        if model not in self._registry:
            return
        if hasattr(instance, '__moderation_disallowed'):
            instance.delete()
            return
        self._registry[model].email(instance, instance.get_content_object())

moderator = Moderator()