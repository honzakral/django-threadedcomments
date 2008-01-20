from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.newforms.util import ErrorDict
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.safestring import mark_safe
from forms import FreeThreadedCommentForm, ThreadedCommentForm
from models import ThreadedComment, FreeThreadedComment
from utils import JSONResponse, XMLResponse
from copy import deepcopy

def _get_next(request):
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    if not next or next == request.path:
        raise Http404 # No next url was supplied in GET or POST.
    return next

def comment(request, content_type, object_id, parent_id=None, add_messages=True, ajax=False):
    """
    Receives POST data and creates a new ``ThreadedComment`` based upon the 
    specified parameters.

    The part that's the least straightforward is how this redirects afterwards.
    It will try and get the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, it will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, it will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, it will
    redirect to that previous page.
    4. Otherwise, it will redirect to '/'.
    
    If it is an *AJAX* request (either XML or JSON), it will return a serialized
    version of the last created ``ThreadedComment`` and there will be no redirect.
    
    If invalid POST data is submitted, this will return an *Http404* error.
    """
    form = ThreadedCommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
        new_comment.content_type = get_object_or_404(ContentType, id = int(content_type))
        new_comment.object_id = int(object_id)
        new_comment.user = request.user
        if parent_id:
            new_comment.parent = get_object_or_404(ThreadedComment, id = int(parent_id))
        new_comment.save()
        if add_messages:
            request.user.message_set.create(message="Your message has been posted successfully.")
        if ajax == 'json':
            return JSONResponse([new_comment,])
        elif ajax == 'xml':
            return XMLResponse([new_comment,])
        else:
            return HttpResponseRedirect(_get_next(request))
    else:
        if add_messages:
            for error in form.errors:
                request.user.message_set.create(message=error)
# Require login to be required, as request.user must exist and be valid.
comment = login_required(comment)

def free_comment(request, content_type, object_id, parent_id=None, ajax=False):
    """
    Receives POST data and creates a new ``FreeThreadedComment`` based upon the 
    specified parameters.
    
    The part that's the least straightforward is how this redirects afterwards.
    It will try and get the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, it will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, it will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, it will
    redirect to that previous page.
    4. Otherwise, it will redirect to '/'.
    
    If it is an *AJAX* request (either XML or JSON), it will return a serialized
    version of the last created ``FreeThreadedComment`` and there will be no 
    redirect.
    
    If invalid POST data is submitted, this will return an *Http404* error.
    """
    form = FreeThreadedCommentForm(request.POST or None, error_class=ErrorDict)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
        new_comment.content_type = get_object_or_404(ContentType, id = int(content_type))
        new_comment.object_id = int(object_id)
        if parent_id:
            new_comment.parent = get_object_or_404(FreeThreadedComment, id = int(parent_id))
        new_comment.save()
        if ajax == 'json':
            return JSONResponse([new_comment,])
        elif ajax == 'xml':
            return XMLResponse([new_comment,])
        else:
            return HttpResponseRedirect(_get_next(request))
    else:
        request.session['errors'] = dict([(smart_unicode(e), [force_unicode(f) for f in form.errors[e]]) for e in form.errors])
        return HttpResponseRedirect(_get_next(request))