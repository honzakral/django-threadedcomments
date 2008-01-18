from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from threadedcomments.models import ThreadedComment, FreeThreadedComment

def get_contenttype_kwargs(content_object):
    kwargs = {
        'content_type' : ContentType.objects.get_for_model(content_object).id,
        'object_id' : getattr(content_object, 'pk', getattr(content_object, 'id')),
    }
    return kwargs

def get_comment_url(content_object, parent=None):
    kwargs = get_contenttype_kwargs(content_object)
    if parent:
        kwargs.update({'parent_id' : getattr(parent, 'pk', getattr(parent, 'id'))})
    return reverse('tc_comment', kwargs=kwargs)

def get_comment_url_ajax(content_object, parent=None, ajax_type='json'):
    kwargs = get_contenttype_kwargs(content_object)
    kwargs.update({'ajax' : ajax_type})
    if parent:
        kwargs.update({'parent_id' : getattr(parent, 'pk', getattr(parent, 'id'))})
    return reverse('tc_comment_ajax', kwargs=kwargs)

def get_comment_url_json(content_object, parent=None):
    return get_comment_url_ajax(content_object, parent, ajax_type="json")

def get_comment_url_xml(content_object, parent=None):
    return get_comment_url_ajax(content_object, parent, ajax_type="xml")

def get_free_comment_url(content_object, parent=None):
    kwargs = get_contenttype_kwargs(content_object)
    if parent:
        kwargs.update({'parent_id' : getattr(parent, 'pk', getattr(parent, 'id'))})
    return reverse('tc_free_comment', kwargs=kwargs)

def get_free_comment_url_ajax(content_object, parent=None, ajax_type='json'):
    kwargs = get_contenttype_kwargs(content_object)
    kwargs.update({'ajax' : ajax_type})
    if parent:
        kwargs.update({'parent_id' : getattr(parent, 'pk', getattr(parent, 'id'))})
    return reverse('tc_free_comment_ajax', kwargs=kwargs)

def get_free_comment_url_json(content_object, parent=None):
    return get_free_comment_url_ajax(content_object, parent, ajax_type="json")

def get_free_comment_url_xml(content_object, parent=None):
    return get_free_comment_url_ajax(content_object, parent, ajax_type="xml")

def do_get_threaded_comment_tree(parser, token):
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag must be of format {%% get_threaded_comment_tree for OBJECT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    return CommentTreeNode(split[2], split[4])

def do_get_free_threaded_comment_tree(parser, token):
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag must be of format {%% get_free_threaded_comment_tree for OBJECT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    return FreeCommentTreeNode(split[2], split[4])

class CommentTreeNode(template.Node):
    def __init__(self, content_object, context_name):
        self.content_object = template.Variable(content_object)
        self.context_name = context_name
    def render(self, context):
        content_object = self.content_object.resolve(context)
        context[self.context_name] = ThreadedComment.public.get_tree(content_object)
        return ''

class FreeCommentTreeNode(template.Node):
    def __init__(self, content_object, context_name):
        self.content_object = template.Variable(content_object)
        self.context_name = context_name
    def render(self, context):
        content_object = self.content_object.resolve(context)
        context[self.context_name] = FreeThreadedComment.public.get_tree(content_object)
        #return ''

def auto_transform_markup(comment):
    try:
        from django.contrib import markup
        from models import MARKDOWN, TEXTILE, REST, HTML, PLAINTEXT
        if comment.markup == MARKDOWN:
            return markup.markdown(comment.comment)
        elif comment.markup == TEXTILE:
            return markup.textile(comment.comment)
        elif comment.markup == REST:
            return markup.restructuredtext(comment.comment)
        elif comment.markup == HTML:
            return mark_safe(force_unicode(comment.comment))
        elif comment.markup == PLAINTEXT:
            return force_unicode(comment.comment)
    except ImportError:
        return force_unicode(comment.comment)

register = template.Library()
register.simple_tag(get_comment_url)
register.simple_tag(get_comment_url_json)
register.simple_tag(get_comment_url_xml)
register.simple_tag(get_free_comment_url)
register.simple_tag(get_free_comment_url_json)
register.simple_tag(get_free_comment_url_xml)

register.simple_tag(auto_transform_markup)

register.tag('get_threaded_comment_tree', do_get_threaded_comment_tree)
register.tag('get_free_threaded_comment_tree', do_get_free_threaded_comment_tree)