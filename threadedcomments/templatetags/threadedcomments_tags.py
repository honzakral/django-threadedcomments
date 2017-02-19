from django import template
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from threadedcomments.compat import BASE_APP, django_comments as comments
from threadedcomments.util import annotate_tree_properties, fill_tree as real_fill_tree

if BASE_APP == 'django.contrib.comments':
    from django.contrib.comments.templatetags.comments import BaseCommentNode
elif BASE_APP == 'django_comments':
    from django_comments.templatetags.comments import BaseCommentNode
else:
    raise NotImplementedError()


register = template.Library()


class AdminOverrideCommentNode(BaseCommentNode):

    def get_queryset(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type=ctype,
            object_pk=smart_text(object_pk),
            site__pk=settings.SITE_ID,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.comment_model._meta.fields]
        if not self.admin:
            if 'is_public' in field_names:
                qs = qs.filter(is_public=True)
            if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
                qs = qs.filter(is_removed=False)

        return qs


class BaseThreadedCommentNode(AdminOverrideCommentNode):

    def __init__(self, parent=None, flat=False, root_only=False, newest=False, limit=False, admin=False, **kwargs):
        self.parent = parent
        self.flat = flat
        self.root_only = root_only
        self.newest = newest
        self.limit = limit
        self.admin = admin
        super(BaseThreadedCommentNode, self).__init__(**kwargs)

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if len(tokens) > 2:
            if tokens[1] != 'for':
                raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        extra_kw = {}
        if tokens[-1] in ('flat', 'root_only', 'newest', 'admin'):
            extra_kw[str(tokens.pop())] = True

        if len(tokens) == 5:
            # {% get_whatever for obj as varname %}
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Fourth argument in %r must be 'as'" % tokens[0])

            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
                **extra_kw
            )
        elif len(tokens) == 6:
            # {% get_whatever for app.model pk as varname %}
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError("Fourth argument in %r must be 'as'" % tokens[0])

            return cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5],
                **extra_kw
            )
        else:
            raise template.TemplateSyntaxError("%r tag takes either 5 or 6 arguments" % (tokens[0],))

    def get_queryset(self, context):
        qs = super(BaseThreadedCommentNode, self).get_queryset(context)
        if self.limit:
            parent_qs = qs.exclude(parent__isnull=False).order_by('-newest_activity', '-submit_date').values_list('pk', flat=True)[:self.limit]
            qs = qs.filter(Q(parent_id__in=parent_qs) | Q(pk__in=parent_qs)).distinct()
        if self.flat:
            qs = qs.order_by('-submit_date')
        elif self.root_only:
            qs = qs.exclude(parent__isnull=False).order_by('-submit_date')
        elif self.newest:
            qs = qs.order_by('-newest_activity', 'tree_path')
        return qs


class CommentListNode(BaseThreadedCommentNode):
    """
    Insert a list of comments into the context.
    """

    def get_context_value_from_queryset(self, context, qs):
        return list(qs)


class CommentCountNode(CommentListNode):
    """
    Insert a count of comments into the context.
    """

    def get_context_value_from_queryset(self, context, qs):
        return qs.count()


class CommentFormNode(BaseThreadedCommentNode):
    """
    Insert a form for the comment model into the context.
    """
    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % (tokens[0],))

        if len(tokens) < 7:
            # Default get_comment_form code
            return super(CommentFormNode, cls).handle_token(parser, token)
        elif len(tokens) == 7:
            # {% get_comment_form for [object] as [varname] with [parent_id] %}
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have a 'with' as the last but one argument." % (tokens[0],))
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                as_varname=tokens[4],
                parent=parser.compile_filter(tokens[6]),
            )
        elif len(tokens) == 8:
            # {% get_comment_form for [app].[model] [object_id] as [varname] with [parent_id] %}
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have a 'with' as the last but one argument." % (tokens[0],))
            return cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5],
                parent=parser.compile_filter(tokens[7]),
            )

    def get_form(self, context):
        parent_id = None
        if self.parent:
            parent_id = self.parent.resolve(context, ignore_failures=True)

        obj = self.get_object(context)
        if obj:
            return comments.get_form()(obj, parent=parent_id)
        else:
            return None

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None
        else:
            object_pk = self.object_pk_expr.resolve(context, ignore_failures=True)
            return self.ctype.get_object_for_this_type(pk=object_pk)

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''


class RenderCommentFormNode(CommentFormNode):

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse render_comment_form and return a Node.
        """
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        if len(tokens) == 3:
            # {% render_comment_form for obj %}
            return cls(object_expr=parser.compile_filter(tokens[2]))
        elif len(tokens) == 4:
            # {% render_comment_form for app.model object_pk %}
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )
        elif len(tokens) == 5:
            # {% render_comment_form for obj with parent_id %}
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have 'with' as the last but one argument" % (tokens[0],))
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                parent=parser.compile_filter(tokens[4])
            )
        elif len(tokens) == 6:
            # {% render_comment_form for app.model object_pk with parent_id %}
            if tokens[-2] != u'with':
                raise template.TemplateSyntaxError("%r tag must have 'with' as the last but one argument" % (tokens[0],))
            return cls(
                ctype=BaseThreadedCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                parent=parser.compile_filter(tokens[5])
            )
        else:
            raise template.TemplateSyntaxError("%r tag takes 2 to 5 arguments" % (tokens[0],))

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = (
                "comments/%s/%s/form.html" % (ctype.app_label, ctype.model),
                "comments/%s/form.html" % ctype.app_label,
                "comments/form.html",
            )
            context = context.flatten()
            context['form'] = self.get_form(context)
            return render_to_string(template_search_list, context)
        else:
            return ''


class RenderCommentListNode(CommentListNode):
    """
    Render the comments list.
    """
    # By having this class added, this module is a drop-in replacement for ``{% load comments %}``.

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        extra_kw = {}
        if tokens[-2] == 'limit':
            if tokens[-1].isdigit():
                extra_kw['limit'] = tokens.pop(-1)  # removes limit integer
                tokens.pop(-1)  # removes 'limit'
            else:
                raise template.TemplateSyntaxError(
                    "When using 'limit' with %r tag, it needs to be followed by a positive integer" % (tokens[0],))
        if tokens[-1] in ('flat', 'root_only', 'newest', 'admin'):
            extra_kw[str(tokens.pop())] = True

        if len(tokens) == 3:
            # {% render_comment_list for obj %}
            return cls(
                object_expr=parser.compile_filter(tokens[2]),
                **extra_kw
            )
        elif len(tokens) == 4:
            # {% render_comment_list for app.models pk %}
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3]),
                **extra_kw
            )
        else:
            raise template.TemplateSyntaxError("%r tag takes either 2 or 3 arguments" % (tokens[0],))

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/list.html" % (ctype.app_label, ctype.model),
                "comments/%s/list.html" % ctype.app_label,
                "comments/list.html"
            ]
            qs = self.get_queryset(context)
            context = context.flatten()
            context.update({
                "comment_list": self.get_context_value_from_queryset(context, qs),
            })
            return render_to_string(template_search_list, context)
        else:
            return ''


@register.tag
def get_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_count for [object] as [varname]  %}
        {% get_comment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_count for event as comment_count %}
        {% get_comment_count for calendar.event event.id as comment_count %}
        {% get_comment_count for calendar.event 17 as comment_count %}

    """
    return CommentCountNode.handle_token(parser, token)


@register.tag
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


@register.tag
def render_comment_list(parser, token):
    """
    Render the comment list (as returned by ``{% get_comment_list %}``)
    through the ``comments/list.html`` template

    Syntax::

        {% render_comment_list for [object] %}
        {% render_comment_list for [app].[model] [object_id] %}

        {% render_comment_list for [object] [flat|root_only] %}
        {% render_comment_list for [app].[model] [object_id] [flat|root_only] %}

    Example usage::

        {% render_comment_list for event %}

    """
    return RenderCommentListNode.handle_token(parser, token)


@register.tag
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


@register.tag
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


@register.filter
def annotate_tree(comments):
    """
    Add ``open``, ``close`` properties to the comments, to render the tree.

    Syntax::

        {% for comment in comment_list|annotate_tree %}
            {% ifchanged comment.parent_id %}{% else %}</li>{% endifchanged %}
            {% if not comment.open and not comment.close %}</li>{% endif %}
            {% if comment.open %}<ul>{% endif %}

            <li id="c{{ comment.id }}">
                ...
            {% for close in comment.close %}</li></ul>{% endfor %}
        {% endfor %}

    When the :func:`fill_tree` filter, place the ``annotate_tree`` code after it::

        {% for comment in comment_list|fill_tree|annotate_tree %}
            ...
        {% endfor %}
    """
    return annotate_tree_properties(comments)


@register.filter
def fill_tree(comments):
    """
    When paginating the comments, insert the parent nodes of the first comment.

    Syntax::

        {% for comment in comment_list|annotate_tree %}
            ...
        {% endfor %}
    """
    return real_fill_tree(comments)
