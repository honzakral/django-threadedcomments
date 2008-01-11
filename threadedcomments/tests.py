"""
##################################
### Model and Moderation Tests ###
##################################
>>> import datetime
>>> from models import FreeThreadedComment, ThreadedComment, Vote, FreeVote, TestModel
>>> from django.contrib.auth.models import User
>>> from django.contrib.contenttypes.models import ContentType
>>> from moderation import moderator, ThreadedCommentModerator

>>> topic = TestModel.objects.create(name = "Test")
>>> user = User.objects.create_user('user', 'floguy@gmail.com', password='password')
>>> user2 = User.objects.create_user('user2', 'floguy@gmail.com', password='password')
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

############################
### Views and URLs Tests ###
############################
>>> from django.core.urlresolvers import reverse
>>> from django.test.client import Client

>>> topic = TestModel.objects.create(name = "Test2")
>>> content_type = ContentType.objects.get_for_model(topic)
  ###########################################
  ### FreeThreadedComments URLs Testsests ###
  ###########################################
>>> c = Client()

>>> url = reverse('tc_free_comment', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: text/html; charset=utf-8
Location: http://testserver/
<BLANKLINE>
<BLANKLINE>

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: application/json
<BLANKLINE>
[{"pk": 2, "model": "threadedcomments.freethreadedcomment", "fields": {"website": "http:\/\/www.eflorenzano.com\/", "comment": "test", "name": "eric", "parent": null, "date_modified":\
...

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: application/xml
<BLANKLINE>
<?xml version="1.0" encoding="utf-8"?>
<django-objects version="1.0"><object pk="3" model="threadedcomments.freethreadedcomment"><field to="contenttypes.contenttype" name="content_type" rel="ManyToOneRel">8</field><field type="PositiveIntegerField" name="object_id">2</field><field to="threadedcomments.freethreadedcomment" name="parent" rel="ManyToOneRel"><None></None></field><field type="CharField" name="name">eric</field><field type="CharField" name="website">http://www.eflorenzano.com/</field><field type="CharField" name="email">floguy@gmail.com</field>\
...

>>> parent = FreeThreadedComment.objects.get_tree(topic)[0]

>>> url = reverse('tc_free_comment_parent', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: text/html; charset=utf-8
Location: http://testserver/
<BLANKLINE>
<BLANKLINE>

>>> url = reverse('tc_free_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: application/json
<BLANKLINE>
[{"pk": 5, "model": "threadedcomments.freethreadedcomment", "fields": {"website": "http:\/\/www.eflorenzano.com\/", "comment": "test", "name": "eric", "parent": 1, "date_modified":\
...

>>> url = reverse('tc_free_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> print response
Content-Type: application/xml
<BLANKLINE>
<?xml version="1.0" encoding="utf-8"?>
<django-objects version="1.0"><object pk="6" model="threadedcomments.freethreadedcomment"><field to="contenttypes.contenttype" name="content_type" rel="ManyToOneRel">8</field><field type="PositiveIntegerField" name="object_id">2</field><field to="threadedcomments.freethreadedcomment" name="parent" rel="ManyToOneRel">1</field><field type="CharField" name="name">eric</field><field type="CharField" name="website">http://www.eflorenzano.com/</field><field type="CharField" name="email">floguy@gmail.com</field>\
...


  #######################################
  ### ThreadedComments URLs Testsests ###
  #######################################
>>> User.objects.create_user('testuser', 'testuser@gmail.com', password='password')
<User: testuser>
>>> c = Client()
>>> c.login(username='testuser', password='password')
True
>>> 1 == 2
False
"""