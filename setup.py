from distutils.core import setup

kwargs = {
    'name' : 'django-threadedcomments',
    'version' : '0.5.1',
    'description' : 'A simple yet flexible threaded commenting system.',
    'author' : 'Eric Florenzano',
    'author_email' : 'floguy@gmail.com',
    'url' : 'http://code.google.com/p/django-threadedcomments/',
    'packages' : ['threadedcomments',
                  'threadedcomments.templatetags',
                  'threadedcomments.management',
                  'threadedcomments.management.commands'],
    'classifiers' : ['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Utilities'],
}
from sys import version_info
if version_info[1] >= 4:
    kwargs['package_data'] = {'threadedcomments' : ['templates/comment_utils/*.txt','templates/threadedcomments/*.html','templates/threadedcomments_base.html']}
setup(**kwargs)
