"""
>>> from models import ThreadedComment, Vote
>>> from django.contrib.auth.models import User
>>> from django.contrib.contenttypes.models import ContentType

>>> user = User.objects.create_user('user', 'floguy@gmail.com', 'password')
>>> user2 = User.objects.create_user('user2', 'floguy@gmail.com', 'password')
>>> content_type = ContentType.objects.get_for_model(user)
>>> comment1 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = 'This is fun!  This is very fun!',
...     ip_address = '127.0.0.1',
... )
>>> comment1.save()
>>> comment2 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = 'This is stupid!  I hate it!',
...     ip_address = '127.0.0.1',
... )
>>> comment2.save()
>>> comment3 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = 'I agree, the first comment was wrong and you are right!',
...     ip_address = '127.0.0.1',
...     parent = comment2,
... )
>>> comment3.save()
>>> comment4 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = 'What are we talking about?',
...     ip_address = '127.0.0.1',
... )
>>> comment4.save()
>>> comment5 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = "I'm a fanboy!",
...     ip_address = '127.0.0.1',
...     parent = comment3,
... )
>>> comment5.save()
>>> comment6 = ThreadedComment(
...     user = user,
...     content_type = content_type,
...     object_id = user.id,
...     comment = "What are you talking about?",
...     ip_address = '127.0.0.1',
...     parent = comment1,
... )
>>> comment6.save()

>>> tree = ThreadedComment.public.get_tree(user)
>>> for comment in tree:
...     print "%s %s" % ("    " * comment.depth, comment.comment)
 This is fun!  This is very fun!
     What are you talking about?
 This is stupid!  I hate it!
     I agree, the first comment was wrong and you are right!
         I'm a fanboy!
 What are we talking about?
"""