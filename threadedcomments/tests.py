"""
### MODEL TESTS ###

>>> import datetime
>>> from models import ThreadedComment, Vote, TestModel
>>> from django.contrib.auth.models import User
>>> from django.contrib.contenttypes.models import ContentType
>>> from moderation import moderator, ThreadedCommentModerator

>>> topic = TestModel(name = "Test")
>>> topic.save()
>>> user = User.objects.create_user('user', 'floguy@gmail.com', 'password')
>>> user2 = User.objects.create_user('user2', 'floguy@gmail.com', 'password')
>>> comment1 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = 'This is fun!  This is very fun!',
...     ip_address = '127.0.0.1',
... )
>>> comment2 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = 'This is stupid!  I hate it!',
...     ip_address = '127.0.0.1',
... )
>>> comment3 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = 'I agree, the first comment was wrong and you are right!',
...     ip_address = '127.0.0.1',
...     parent = comment2,
... )
>>> comment4 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = 'What are we talking about?',
...     ip_address = '127.0.0.1',
... )
>>> comment5 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "I'm a fanboy!",
...     ip_address = '127.0.0.1',
...     parent = comment3,
... )
>>> comment6 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "What are you talking about?",
...     ip_address = '127.0.0.1',
...     parent = comment1,
... )

>>> class TestModerator(ThreadedCommentModerator):
...     enable_field = 'is_public'
...     auto_close_field = 'date'
...     close_after = 15
>>> moderator.register(TestModel, TestModerator)

>>> comment7 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "Post moderator addition.  Does it still work?",
...     ip_address = '127.0.0.1',
... )

>>> topic.is_public = False
>>> topic.save()

>>> comment8 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This should not appear, due to auto_close_field",
...     ip_address = '127.0.0.1',
...     parent = comment7,
... )

>>> topic.is_public = True
>>> topic.save()

>>> comment9 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This should appear again.",
...     ip_address = '127.0.0.1',
...     parent = comment1,
... )

>>> topic.date = topic.date - datetime.timedelta(days = 20)
>>> topic.save()

>>> comment10 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This shouldn't appear, due to close_after=15.",
...     ip_address = '127.0.0.1',
...     parent = comment7,
... )

>>> tree = ThreadedComment.public.get_tree(topic)
>>> for comment in tree:
...     print "%s %s" % ("    " * comment.depth, comment.comment)
 This is fun!  This is very fun!
     What are you talking about?
     This should appear again.
 This is stupid!  I hate it!
     I agree, the first comment was wrong and you are right!
         I'm a fanboy!
 What are we talking about?
 Post moderator addition.  Does it still work?

>>> tree = ThreadedComment.objects.get_tree(topic)
>>> for comment in tree:
...     print "%s %s" % ("    " * comment.depth, comment.comment)
 This is fun!  This is very fun!
     What are you talking about?
     This should appear again.
 This is stupid!  I hate it!
     I agree, the first comment was wrong and you are right!
         I'm a fanboy!
 What are we talking about?
 Post moderator addition.  Does it still work?

### FORM TESTS ###

>>> from forms import ThreadedCommentForm, VoteForm
>>> data = {'parent' : comment1.parent, 'comment' : comment1.comment, 'object_id' : comment1.object_id, 'content_type' : comment1.content_type.id, 'user' : user.id}
>>> form = ThreadedCommentForm(data, instance = comment1)
>>> form.is_valid()
True
>>> form.cleaned_data
{'parent': None, 'comment': u'This is fun!  This is very fun!', 'object_id': 1, 'content_type': 10, 'user': <User: user>}
>>> print form
<tr><th><label for="id_comment">Comment:</label></th><td><textarea id="id_comment" rows="10" cols="40" name="comment">This is fun!  This is very fun!</textarea><input type="hidden" name="content_type" value="10" id="id_content_type" /><input type="hidden" name="object_id" value="1" id="id_object_id" /><input type="hidden" name="parent" id="id_parent" /><input type="hidden" name="user" value="1" id="id_user" /></td></tr>

>>> data = {'user' : user.id, 'comment' : comment1.id, 'vote' : '+1'}
>>> form = VoteForm({})
>>> form.is_valid()
False
>>> form.errors
{'comment': [u'This field is required.'], 'vote': [u'This field is required.'], 'user': [u'This field is required.']}
>>> form = VoteForm(data)
>>> form.is_valid()
True
>>> form.save()
<Vote: Vote object>
"""