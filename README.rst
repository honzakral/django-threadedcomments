django-threadedcomments
=======================

*threadedcomments* is a Django application which allows for the simple creation of a threaded commenting system.
Commenters can reply both to the original item, and reply to other comments as well.

The application is built on top of django_comments_,
which allows it to be easily extended by other modules.


Installation
============

Install the package via pip::

    pip install django-threadedcomments

It's preferred to install the module in a virtual environment.

Configuration
-------------

Add the following to ``settings.py``::

    INSTALLED_APPS += (
        'threadedcomments',
        'django_comments',
        'django.contrib.sites',
    )

    COMMENTS_APP = 'threadedcomments'

By placing the ``threadedcomments`` app above the ``django.contrib.comments`` application,
the placeholder ``comments/list.html`` template will already be replaced by a threaded view.

Make sure django_comments_ is configured in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^articles/comments/', include('django_comments.urls')),
    )

Provide a template that displays the comments for the ``object`` (e.g. article or blog entry)::

    {% load threadedcomments_tags %}

    ...

    <h2>Comments for {{ object.title }}:</h2>

    {% render_comment_list for object %}
    {% render_comment_form for object %}


Template design
---------------

Naturally, it's desirable to write your own version of ``comments/list.html`` in your project,
or use one of the ``comments/app/list.html`` or ``comments/app/model/list.html`` overrides.

Make sure to override ``comments/base.html`` as well, so the other views of django_comments_
are displayed using your web site design. The other templates of django_comments_ are
very plain as well on purpose (for example ``comments/posted.html``),
since these pages depend on the custom design of the web site.

See the provided ``example`` app for a basic configuration,
including a JavaScript-based reply form that moves to the comment the visitor replies to.


Template tags
=============

The ``threadedcomments_tags`` library is a drop-in replacement for the ``comments`` library
that is required for the plain comments. The tags are forwards compatible;
they support the same syntax as django_comments_ provides,
and they add a few extra parameters.

Fetching comment counts::

    {% get_comment_count for [object] as [varname] %}
    {% get_comment_count for [object] as [varname] root_only %}

    {% get_comment_count for [app].[model] [id] as [varname] %}
    {% get_comment_count for [app].[model] [id] as [varname] root_only %}

Fetching the comments list::

    {% get_comment_list for [object] as [varname] %}
    {% get_comment_list for [object] as [varname] flat %}
    {% get_comment_list for [object] as [varname] root_only %}

Rendering the comments list::

    {% render_comment_list for [object] %}
    {% render_comment_list for [object] root_only %}

    {% render_comment_list for [app].[model] [id] %}
    {% render_comment_list for [app].[model] [id] root_only %}

Fetching the comment form::

    {% get_comment_form for [object] as [varname] %}
    {% get_comment_form for [object] as [varname] with [parent_id] %}
    {% get_comment_form for [app].[model] [id] as [varname] %}
    {% get_comment_form for [app].[model] [id] as [varname] with [parent_id] %}

Rendering the comment form::

    {% render_comment_form for [object] %}
    {% render_comment_form for [object] with [parent_id] %}
    {% render_comment_form for [app].[model] [id] %}
    {% render_comment_form for [app].[model] [id] with [parent_id] %}

Rendering the whole tree::

    {% for comment in comment_list|fill_tree|annotate_tree %}
        {% ifchanged comment.parent_id %}{% else %}</li>{% endifchanged %}
        {% if not comment.open and not comment.close %}</li>{% endif %}
        {% if comment.open %}<ul>{% endif %}

        <li id="c{{ comment.id }}">
            ...
        {% for close in comment.close %}</li></ul>{% endfor %}
    {% endfor %}

The ``fill_tree`` filter is required for pagination, it ensures that the parents of the first comment are included as well.

The ``annotate_tree`` filter adds the ``open`` and ``close`` properties to the comment.


Extending the module
====================

The application is built on top of the standard django_comments_ framework,
which supports various signals, and template overrides to customize the comments.

To customize django-threadedcomments, override the proper templates, or include the apps that provide the missing features.
Front-end editing support for example, is left out on purpose. It belongs to the domain of moderation, and policies
to know "who can do what". That deserves to be in a separate application, it shouldn't be in this application as it focuses on threading.
The same applies to social media logins, comment subscriptions, spam protection and Ajax posting.

Note that the standard framework also supports moderation, flagging, and RSS feeds too. More documentation can be found at:

* `Django's comments framework <https://django-contrib-comments.readthedocs.io/>`_
* `Customizing the comments framework <https://django-contrib-comments.readthedocs.io/en/latest/custom.html>`_
* `Example of using the in-built comments app <https://django-contrib-comments.readthedocs.io/en/latest/example.html>`_

Some of the modules worth looking at are:

* django-comments-spamfighter_
* django-myrecaptcha_
* django-fluent-comments_

These modules can enhance the comments system even further.


.. _django_comments: https://github.com/django/django-contrib-comments
.. _django-fluent-comments: https://github.com/edoburu/django-fluent-comments/
.. _django-myrecaptcha: https://bitbucket.org/pelletier/django-myrecaptcha/
.. _django-comments-spamfighter: https://github.com/bartTC/django-comments-spamfighter/
