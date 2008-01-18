from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson

class JSONResponse(HttpResponse):
    """
    A simple subclass of ``HttpResponse`` which makes serializing to JSON easy.
    """
    def __init__(self, object):
        if hasattr(object, '__iter__'):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(object)
        super(JSONResponse, self).__init__(content, mimetype='application/json')

class XMLResponse(HttpResponse):
    """
    A simple subclass of ``HttpResponse`` which makes serializing to XML easy.
    """
    def __init__(self, object):
        super(XMLResponse, self).__init__(serialize('xml', object), mimetype='application/xml')