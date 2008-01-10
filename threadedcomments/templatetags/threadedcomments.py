from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from threadedcomments.models import ThreadedComment, FreeThreadedComment

#def get_contenttype_kwargs(content_object):
    #kwargs = {
        #'content_type' : ContentType.objects.get_for_model(content_object),
        #'object_id' : getattr(content_object, 'pk', getattr(content_object, 'id')),
    #}
    #return kwargs

#def get_comment_url(content_object, parent=None):
    #kwargs = get_contenttype_kwargs(content_object)
    #if parent:
        #kwargs.update({'parent' : parent})
    #return reverse('tc_comment', kwargs=kwargs)

#def get_comment_url_ajax(content_object, parent=None):
    #kwargs = get_contenttype_kwargs(content_object)
    #kwargs.update({'ajax' : 'ajax'})
    #if parent:
        #kwargs.update({'parent' : parent})
    #return reverse('tc_comment_ajax', kwargs=kwargs)

#def get_free_comment_url(content_object, parent=None):
    #kwargs = get_contenttype_kwargs(content_object)
    #if parent:
        #kwargs.update({'parent' : parent})
    #return reverse('tc_free_comment', kwargs=kwargs)

#def get_free_comment_url_ajax(content_object, parent=None):
    #kwargs = get_contenttype_kwargs(content_object)
    #kwargs.update({'ajax' : 'ajax'})
    #if parent:
        #kwargs.update({'parent' : parent})
    #return reverse('tc_free_comment_ajax', kwargs=kwargs)

#def do_get_threaded_comment_tree(parser, token):
    #try:
        #split = token.split_contents()
    #except ValueError:
        #raise template.TemplateSyntaxError, "%r tag must be of format {%% get_threaded_comment_tree for OBJECT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    #return CommentTreeNode(split[2], split[4])

#def do_get_free_threaded_comment_tree(parser, token):
    #try:
        #split = token.split_contents()
    #except ValueError:
        #raise template.TemplateSyntaxError, "%r tag must be of format {%% get_free_threaded_comment_tree for OBJECT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    #return FreeCommentTreeNode(split[2], split[4])

#class CommentTreeNode(template.Node):
    #def __init__(self, content_object, context_name):
        #self.content_object = template.Variable(content_object)
        #self.context_name = context_name
    #def render(self, context):
        #content_object = self.content_object.resolve(context)
        #context[self.context_name] = ThreadedComment.public.get_tree(content_object)
        #return ''

#class FreeCommentTreeNode(template.Node):
    #def __init__(self, content_object, context_name):
        #self.content_object = template.Variable(content_object)
        #self.context_name = context_name
    #def render(self, context):
        #content_object = self.content_object.resolve(context)
        #context[self.context_name] = FreeThreadedComment.public.get_tree(content_object)
        #return ''

register = template.Library()
#register.simple_tag(get_comment_url)
#register.simple_tag(get_comment_url_ajax)
#register.simple_tag(get_free_comment_url)
#register.simple_tag(get_free_comment_url_ajax)

#register.tag('get_threaded_comment_tree', do_get_threaded_comment_tree)
#register.tag('get_free_threaded_comment_tree', do_get_free_threaded_comment_tree)