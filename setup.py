from sys import version_info
from setuptools import setup

kwargs = {
    'name': 'django-threadedcomments',
    'version': '0.5.4',
    'description': 'A simple yet flexible threaded commenting system.',
    'author': 'Eric Florenzano',
    'author_email': 'floguy@gmail.com',
    'url': 'https://github.com/HonzaKral/django-threadedcomments/',
    'keywords': 'django,pinax,comments',
    'license': 'BSD',
    'packages': [
        'threadedcomments',
        'threadedcomments.templatetags',
        'threadedcomments.management',
        'threadedcomments.management.commands',
    ],
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
}
if version_info[1] >= 4:
    kwargs['package_data'] = {
        'threadedcomments' : [
            'sql/threadedcomment.mysql.sql',
            'fixtures/simple_tree.json',
        ]
    }
setup(**kwargs)
