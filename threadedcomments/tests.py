"""
##################################
### Model and Moderation Tests ###
##################################
>>> import datetime
>>> from models import FreeThreadedComment, ThreadedComment, Vote, FreeVote, TestModel
>>> from django.contrib.auth.models import User
>>> from django.contrib.contenttypes.models import ContentType
>>> from moderation import moderator
>>> from django.core import mail

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

>>> moderator.register(TestModel, enable_field='is_public', auto_close_field='date', close_after=15)

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
...     comment = "This should not appear, due to enable_field",
...     ip_address = '127.0.0.1',
...     parent = comment7,
... )

>>> moderator.unregister(TestModel)

>>> comment9 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This should appear again, due to unregistration",
...     ip_address = '127.0.0.1',
...     parent = None,
... )

>>> len(mail.outbox)
0

>>> class Manager(object):
...     enable_field = 'is_public'
...     auto_close_field = 'date'
...     close_after = 15
...     akismet = False
...     email_notification = True
>>> moderator.register(TestModel, manager=Manager)

>>> comment10 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This should not appear again, due to registration with a new manager.",
...     ip_address = '127.0.0.1',
...     parent = None,
... )

>>> topic.is_public = True
>>> topic.save()

>>> comment11 = ThreadedComment.objects.create_for_object(
...     topic,
...     user = user,
...     comment = "This should appear again.",
...     ip_address = '127.0.0.1',
...     parent = comment1,
... )

>>> len(mail.outbox)
1

>>> topic.date = topic.date - datetime.timedelta(days = 20)
>>> topic.save()

>>> comment12 = ThreadedComment.objects.create_for_object(
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
 This should appear again, due to unregistration

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
 This should appear again, due to unregistration
>>>

############################
### Views and URLs Tests ###
############################
>>> from django.core.urlresolvers import reverse
>>> from django.test.client import Client
>>> from django.utils.simplejson import loads
>>> from xml.dom.minidom import parseString

>>> topic = TestModel.objects.create(name = "Test2")
>>> content_type = ContentType.objects.get_for_model(topic)
>>>
  ###########################################
  ### FreeThreadedComments URLs Testsests ###
  ###########################################
>>> c = Client()

>>> url = reverse('tc_free_comment', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> FreeThreadedComment.objects.latest().get_base_data()
{'website': u'http://www.eflorenzano.com/', 'comment': u'test', 'name': u'eric', 'parent': None, 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = loads(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data()
{'website': u'http://www.eflorenzano.com/', 'comment': u'test', 'name': u'eric', 'parent': None, 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> tmp = parseString(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data()
{'website': u'http://www.eflorenzano.com/', 'comment': u'test', 'name': u'eric', 'parent': None, 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> parent = FreeThreadedComment.objects.latest()

>>> url = reverse('tc_free_comment_parent', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> FreeThreadedComment.objects.latest().get_base_data()
{'website': u'http://www.eflorenzano.com/', 'comment': u'test', 'name': u'eric', 'parent': <FreeThreadedComment: test>, 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = loads(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data()
{'website': u'http://www.eflorenzano.com/', 'comment': u'test', 'name': u'eric', 'parent': <FreeThreadedComment: test>, 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_parent_ajax',
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = parseString(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data()

  #######################################
  ### ThreadedComments URLs Testsests ###
  #######################################
>>> u = User.objects.create_user('testuser', 'testuser@gmail.com', password='password')
>>> u.is_active = True
>>> u.save()
>>> c.login(username='testuser', password='password')
True

>>> url = reverse('tc_comment', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'next' : '/'})
>>> ThreadedComment.objects.latest().get_base_data()

>>> url = reverse('tc_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test'})
>>> tmp = loads(response.content)
>>> ThreadedComment.objects.latest().get_base_data()

>>> url = reverse('tc_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test'})
>>> tmp = parseString(response.content)
>>> ThreadedComment.objects.latest().get_base_data()

>>> parent = ThreadedComment.objects.get_tree(topic)[0]

>>> url = reverse('tc_comment_parent', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id}
... )
>>> response = c.post(url, {'comment' : 'test', 'next' : '/'})
>>> ThreadedComment.objects.latest().get_base_data()

>>> url = reverse('tc_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test'})
>>> tmp = loads(response.content)
>>> ThreadedComment.objects.latest().get_base_data()

>>> url = reverse('tc_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test'})
>>> tmp = parseData(response.content)
>>> ThreadedComment.objects.latest().get_base_data()
>>>
#########################
### Templatetag Tests ###
#########################
>>> from django.template import Context, Template
>>> from threadedcomments.templatetags import threadedcommentstags as tags

>>> topic = TestModel.objects.create(name = "Test3")
>>> c = Context({'topic' : topic, 'parent' : comment9})

>>> Template('{% load threadedcommentstags %}{% get_comment_url topic %}').render(c)
u'/comment/10/3/'

>>> Template('{% load threadedcommentstags %}{% get_comment_url topic parent %}').render(c)
u'/comment/10/3/8/'

>>> Template('{% load threadedcommentstags %}{% get_comment_url_json topic %}').render(c)
u'/comment/10/3/json/'
"""