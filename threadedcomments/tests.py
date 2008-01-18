"""
##################################
### Model and Moderation Tests ###
##################################
>>> import datetime
>>> from models import FreeThreadedComment, ThreadedComment, TestModel
>>> from django.contrib.auth.models import User
>>> from django.contrib.contenttypes.models import ContentType
>>> from moderation import moderator
>>> from django.core import mail

>>> topic = TestModel.objects.create(name = "Test")
>>> user = User.objects.create_user('user', 'floguy@gmail.com', password='password')
>>> user2 = User.objects.create_user('user2', 'floguy@gmail.com', password='password')
>>> comment1 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = 'This is fun!  This is very fun!',
... )
>>> comment2 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = 'This is stupid!  I hate it!',
... )
>>> comment3 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment2,
...     comment = 'I agree, the first comment was wrong and you are right!',
... )
>>> comment4 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = 'What are we talking about?',
... )
>>> comment5 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment3,
...     comment = "I'm a fanboy!",
... )
>>> comment6 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment1,
...     comment = "What are you talking about?",
... )

>>> moderator.register(TestModel, enable_field='is_public', auto_close_field='date', close_after=15)

>>> comment7 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = "Post moderator addition.  Does it still work?",
... )

>>> topic.is_public = False
>>> topic.save()

>>> comment8 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment7,
...     comment = "This should not appear, due to enable_field",
... )

>>> moderator.unregister(TestModel)

>>> comment9 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = "This should appear again, due to unregistration",
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
...     topic, user = user, ip_address = '127.0.0.1',
...     comment = "This should not appear again, due to registration with a new manager.",
... )

>>> topic.is_public = True
>>> topic.save()

>>> comment11 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment1,
...     comment = "This should appear again.",
... )

>>> len(mail.outbox)
1

>>> topic.date = topic.date - datetime.timedelta(days = 20)
>>> topic.save()

>>> comment12 = ThreadedComment.objects.create_for_object(
...     topic, user = user, ip_address = '127.0.0.1', parent = comment7,
...     comment = "This shouldn't appear, due to close_after=15.",
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
>>> old_topic = topic
>>> content_type = ContentType.objects.get_for_model(topic)
>>>
  ###########################################
  ### FreeThreadedComments URLs Testsests ###
  ###########################################
>>> c = Client()

>>> url = reverse('tc_free_comment', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id}
... )
>>> response = c.post(url, {'comment' : 'test1', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test1', 'name': u'eric', 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test2', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = loads(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test2', 'name': u'eric', 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test3', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> tmp = parseString(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test3', 'name': u'eric', 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> parent = FreeThreadedComment.objects.latest()

>>> url = reverse('tc_free_comment_parent', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id}
... )
>>> response = c.post(url, {'comment' : 'test4', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com', 'next' : '/'})
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test4', 'name': u'eric', 'parent': <FreeThreadedComment: test3>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test5', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = loads(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test5', 'name': u'eric', 'parent': <FreeThreadedComment: test3>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

>>> url = reverse('tc_free_comment_parent_ajax',
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test6', 'name' : 'eric', 'website' : 'http://www.eflorenzano.com/', 'email' : 'floguy@gmail.com'})
>>> tmp = parseString(response.content)
>>> FreeThreadedComment.objects.latest().get_base_data(show_dates=False)
{'website': u'http://www.eflorenzano.com/', 'comment': u'test6', 'name': u'eric', 'parent': <FreeThreadedComment: test3>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'is_public': True, 'ip_address': None, 'email': u'floguy@gmail.com', 'is_approved': True}

  ###################################
  ### ThreadedComments URLs Tests ###
  ###################################
>>> u = User.objects.create_user('testuser', 'testuser@gmail.com', password='password')
>>> u.is_active = True
>>> u.save()
>>> c.login(username='testuser', password='password')
True

>>> url = reverse('tc_comment', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id}
... )
>>> response = c.post(url, {'comment' : 'test7', 'next' : '/'})
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test7', 'is_approved': True, 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}

>>> url = reverse('tc_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test8'})
>>> tmp = loads(response.content)
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test8', 'is_approved': True, 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}

>>> url = reverse('tc_comment_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id,
...         'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test9'})
>>> tmp = parseString(response.content)
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test9', 'is_approved': True, 'parent': None, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}

>>> parent = ThreadedComment.objects.latest()

>>> url = reverse('tc_comment_parent', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id}
... )
>>> response = c.post(url, {'comment' : 'test10', 'next' : '/'})
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test10', 'is_approved': True, 'parent': <ThreadedComment: test9>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}

>>> url = reverse('tc_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'json'}
... )
>>> response = c.post(url, {'comment' : 'test11'})
>>> tmp = loads(response.content)
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test11', 'is_approved': True, 'parent': <ThreadedComment: test9>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}

>>> url = reverse('tc_comment_parent_ajax', 
...     kwargs={'content_type': content_type.id, 'object_id' : topic.id, 
...         'parent_id' : parent.id, 'ajax' : 'xml'}
... )
>>> response = c.post(url, {'comment' : 'test12'})
>>> tmp = parseString(response.content)
>>> ThreadedComment.objects.latest().get_base_data(show_dates=False)
{'comment': u'test12', 'is_approved': True, 'parent': <ThreadedComment: test9>, 'markup': 'plaintext', 'content_object': <TestModel: TestModel object>, 'user': <User: testuser>, 'is_public': True, 'ip_address': None}
>>>
#########################
### Templatetag Tests ###
#########################
>>> from django.template import Context, Template
>>> from threadedcomments.templatetags import threadedcommentstags as tags

>>> topic = TestModel.objects.create(name = "Test3")
>>> c = Context({'topic' : topic, 'parent' : comment9})

>>> Template('{% load threadedcommentstags %}{% get_comment_url topic %}').render(c)
u'/comment/9/3/'
>>> Template('{% load threadedcommentstags %}{% get_comment_url topic parent %}').render(c)
u'/comment/9/3/8/'
>>> Template('{% load threadedcommentstags %}{% get_comment_url_json topic %}').render(c)
u'/comment/9/3/json/'
>>> Template('{% load threadedcommentstags %}{% get_comment_url_xml topic %}').render(c)
u'/comment/9/3/xml/'
>>> Template('{% load threadedcommentstags %}{% get_comment_url_json topic parent %}').render(c)
u'/comment/9/3/8/json/'
>>> Template('{% load threadedcommentstags %}{% get_comment_url_xml topic parent %}').render(c)
u'/comment/9/3/8/xml/'

>>> c = Context({'topic' : topic, 'parent' : FreeThreadedComment.objects.latest()})
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url topic %}').render(c)
u'/freecomment/9/3/'
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url topic parent %}').render(c)
u'/freecomment/9/3/6/'
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url_json topic %}').render(c)
u'/freecomment/9/3/json/'
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url_xml topic %}').render(c)
u'/freecomment/9/3/xml/'
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url_json topic parent %}').render(c)
u'/freecomment/9/3/6/json/'
>>> Template('{% load threadedcommentstags %}{% get_free_comment_url_xml topic parent %}').render(c)
u'/freecomment/9/3/6/xml/'

>>> c = Context({'topic' : old_topic, 'parent' : FreeThreadedComment.objects.latest()})
>>> Template('{% load threadedcommentstags %}{% get_free_threaded_comment_tree for topic as tree %}[{% for item in tree %}({{ item.depth }}){{ item.comment }},{% endfor %}]').render(c)
u'[(0)test1,(0)test2,(0)test3,(1)test4,(1)test6,(0)test5,]'

>>> Template('{% load threadedcommentstags %}{% get_threaded_comment_tree for topic as tree %}[{% for item in tree %}({{ item.depth }}){{ item.comment }},{% endfor %}]').render(c)
u'[(0)test7,(0)test8,(0)test9,(1)test10,(1)test12,(0)test11,]'
"""