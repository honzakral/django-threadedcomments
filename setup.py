#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-threadedcomments',
    version='0.9',
    license='BSD',

    description='A simple yet flexible threaded commenting system.',
    long_description=open('README.rst').read(),
    keywords='django,comments,threading',

    author='Eric Florenzano',
    author_email='floguy@gmail.com',

    maintainer='Honza Kral',
    maintainer_email='honza.kral@gmail.com',

    url='https://github.com/HonzaKral/django-threadedcomments',
    download_url='https://github.com/HonzaKral/django-threadedcomments/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
