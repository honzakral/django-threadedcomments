from models import BlogPost
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404
from threadedcomments.forms import FreeThreadedCommentForm

def latest_post(request):
    try:
        post = BlogPost.objects.latest('date_posted')
    except BlogPost.DoesNotExist:
        raise Http404
    errors = request.session.pop('errors', None)
    if errors:
        errors = ["%s: %s" % (e, ' '.join(errors[e])) for e in errors]
    context = {
        'post' : post, 
        'form' : FreeThreadedCommentForm(),
        'errors' : errors,
    }
    return render_to_response(
        'blog/latest_post.html', context,
        context_instance = RequestContext(request)
    )