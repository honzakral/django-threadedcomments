Changes in git
--------------

* Confirmed Django 2.1 support.
* Dropped Django 1.7, 1.8, 1.9, 1.10 support.


Version 1.2, 29 march 2018
--------------------------

* Added Django 2.0 support.


Version 1.1, 19 februari 2017
-----------------------------

* Added Django 1.10 support.
* Added sorting on the latest activity (`{% render_comment_list for [object] newest %}`).
* Dropped Django 1.5, 1.6 support.
* Dropped Python 2.6 support.

Version 1.0.1, 17 October 2015
------------------------------

* Fixed model loading for Django 1.9, avoid importing them in ``__init__.py``.
* Fixed missing transaction management for ``ThreadedComment.save()``

Version 1.0, 1st October 2015
-----------------------------

* Fixed ``RenderCommentListNode.render()`` for Django 1.8
* Fixed MySQL index issue on tree_path
* Fixed updating ``ThreadedComment.last_child`` correctly

Already released in 1.0b1:
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added Django 1.7 and 1.8 support
* Deleting last child should mark it's parent as having no children
* Fixed closing ``</li>`` markup in HTML
* Fixed MySQL issues with migrations, replaced ``TextField`` with ``CharField`` for tree_path

Version 0.9, 15th May 2013
--------------------------

Rewrote application to use django.contrib.comments
Included example app

Version 0.5.1, 31st March 2009
------------------------------

Released version 0.5 of the application and moved the code to GitHub. This is
the last of this line--the next release will be a large rewrite to use the
comment extension hooks provided in Django 1.1 and will be backwards
incompatible.

Version 0.4, 7th March 2008
---------------------------

Added gravatar support, internationalization support on the comment models,
and fixed a bug with get_threaded_comment_form.

Version 0.3.1, 24th February 2008
----------------------------------

Bugfix release, fixed problem with django-comment-utils always being required
and added extra keyword argument onto each of the comment views which allows
for the specification of a custom form.

Version 0.3, 24th February 2008:
---------------------------------

Got rid of proprietary comment moderation tools in favor of the better-designed
django-comment-utils by James Bennett.  Also, provided template tags which get
unbound FreeThreadedCommentForm and ThreadedCommentForm forms.

Version 0.2, 4th February 2008:
---------------------------------

Added the ability to edit or delete comments.  Also added the ability to 
preview comments (like django.contrib.comments does) and confirm deletion of 
comments.

Also fixed a few bugs, one which was major and made it so that redirection
worked improperly after a new ThreadedComment was posted.

Finally, added max_depth as an attribute to the moderation system, so that
someone cannot vandalize the system by posting a long series of replies to
replies.

Version 0.1.1, 24th January 2008:
---------------------------------

Added get_comment_count and get_free_comment_count templatetags.  Also updated
the manager to have a all_for_object method which gets all related objects
to the given content object.


Version 0.1, 23th January 2008:
-------------------------------

Packaged from revision 59 in Subversion; download at
http://django-threadedcomments.googlecode.com/files/threadedcomments-0.1.zip

* First packaged version using distutils.
