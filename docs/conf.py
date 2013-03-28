extensions = ['sphinx.ext.autodoc']
templates_path = ['.templates']
source_suffix = '.txt'
master_doc = 'index'

# General information about the project. Made changes to satisfy 2to3 recommendations.
try:
    #Python 3 with Django 1.5
    project = 'Django threaded comments'
except:
    project = u'Django threaded comments'

