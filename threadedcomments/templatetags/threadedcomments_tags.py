from django import template
from django.template.loader import render_to_string
from django.contrib.comments.templatetags.comments import BaseCommentNode
from django.contrib import comments
from threadedcomments.util import annotate_tree_properties, fill_tree
register = template.Library()

class BaseThreadedCommentNode(BaseCommentNode):
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        super(BaseThreadedCommentNode, self).__init__(**kwargs)

class CommentListNode(BaseThreadedCommentNode):
    """
    Insert a list of comments into the context.
    """

    def __init__(self, flat=False, root_only=False, **kwargs):
        self.flat = flat
        self.root_only = root_only
        super(CommentListNode, self).__init__(**kwargs)

    def handle_token(cls, parser, token):
        tokens = token.contents.split()

        extra_kw = {}
        if tokens[-1] in ('flat', 'root_only'):
            extra_kw[str(tokens.pop())] = True

        if len(tokens) == 5:
            comment_node_instance = cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
                **extra_kw
            )
        elif len(tokens) == 6:
            comment_node_instance = cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2],
                    tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5],
                **extra_kw
            )
        else:
            raise template.TemplateSyntaxError(
                "%r tag takes either 5 or 6 arguments" % (tokens[0],))
        return comment_node_instance

    handle_token = classmethod(handle_token)

    def get_context_value_from_queryset(self, context, qs):
        if self.flat:
            qs = qs.order_by('-submit_date')
        elif self.root_only:
            qs = qs.exclude(parent__isnull=False).order_by('-submit_date')
        return qs


class CommentFormNode(BaseThreadedCommentNode):
    """
    Insert a form for the comment model into the context.
    """
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag "
                "must be 'for'" % (tokens[0],))

        if len(tokens) < 7:
            return super(CommentFormNode, cls).handle_token(parser, token)
        # {% get_comment_form for [object] as [varname] with [parent_id] %}
        if len(tokens) == 7:
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have a 'with' "
                    "as the last but one argument." % (tokens[0],))
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
                parent=parser.compile_filter(tokens[6]),
            )
        # {% get_comment_form for [app].[model] [object_id] as [varname] with [parent_id] %}
        elif len(tokens) == 8:
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have a 'with' "
                    "as the last but one argument." % (tokens[0],))
            return cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2],
                    tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5],
                parent=parser.compile_filter(tokens[7]),
            )

    handle_token = classmethod(handle_token)

    def get_form(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        parent_id = None
        if self.parent:
            parent_id = self.parent.resolve(context, ignore_failures=True)
        if object_pk:
            return comments.get_form()(
                ctype.get_object_for_this_type(pk=object_pk), parent=parent_id)
        else:
            return None

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''

class RenderCommentFormNode(CommentFormNode):
    def handle_token(cls, parser, token):
        """
        Class method to parse render_comment_form and return a Node.
        """
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must"
                " be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))
        # {% render_comment_form for app.model object_pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2],
                    tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )
        # {% render_comment_form for obj with parent_id %}
        elif len(tokens) == 5:
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have 'with' as "
                    "the last but one argument" % (tokens[0],))
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                parent=parser.compile_filter(tokens[4])
            )
        # {% render_comment_form for app.model object_pk with parent_id %}
        elif len(tokens) == 6:
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have 'with' as "
                    "the last but one argument" % (tokens[0],))
            return cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2],
                    tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                parent=parser.compile_filter(tokens[5])
            )
        else:
            raise template.TemplateSyntaxError("%r tag takes 3 to 5 "
                "arguments" % (tokens[0],))

    handle_token = classmethod(handle_token)

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = (
                "comments/%s/%s/form.html" % (ctype.app_label, ctype.model),
                "comments/%s/form.html" % ctype.app_label,
                "comments/form.html",
            )
            context.push()
            form_str = render_to_string(
                template_search_list,
                {"form" : self.get_form(context)},
                context
            )
            context.pop()
            return form_str
        else:
            return ''


def get_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] as [varname] %}
        {% get_comment_list for [object] as [varname] [flat|root_only] %}
        {% get_comment_list for [app].[model] [object_id] as [varname] %}
        {% get_comment_list for [app].[model] [object_id] as [varname] [flat|root_only] %}

    Example usage::

        {% get_comment_list for event as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}
        {% get_comment_list for event as comment_list flat %}

    """
    return CommentListNode.handle_token(parser, token)

def get_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_comment_form for [object] as [varname] %}
        {% get_comment_form for [object] as [varname] with [parent_id] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] with [parent_id] %}
    """
    return CommentFormNode.handle_token(parser, token)

def render_comment_form(parser, token):
    """
    Render the comment form (as returned by ``{% render_comment_form %}``) 
    through the ``comments/form.html`` template.

    Syntax::

        {% render_comment_form for [object] %}
        {% render_comment_form for [object] with [parent_id] %}
        {% render_comment_form for [app].[model] [object_id] %}
        {% render_comment_form for [app].[model] [object_id] with [parent_id] %}
    """
    return RenderCommentFormNode.handle_token(parser, token)



def annotate_tree(comments):
    return annotate_tree_properties(comments)

register.filter(annotate_tree)
register.filter(fill_tree)
register.tag(get_comment_list)
register.tag(get_comment_form)
register.tag(render_comment_form)
