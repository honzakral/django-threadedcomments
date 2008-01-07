from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from forms import ThreadedCommentForm, VoteForm
from models import Vote

def post_comment(request, content_type, object_id, parent=None, add_messages=True, ajax=False):
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META['REMOTE_ADDR']
        new_comment.content_type = int(content_type)
        new_comment.object_id = int(object_id)
        new_comment.user = request.user
        new_comment.save()
        if add_messages:
            request.user.message_set.create(message="Your message has been posted successfully.")
    else:
        if add_messages:
            for error in form.errors:
                request.user.message_set.create(message=error)
    if ajax:
        # TODO: decide whether simplejson is needed
        return HttpResponse('{"comment_posted" : true}', mimetype="application/json")
    else:
        # Determine next url
        if request.method == "POST":
            form = ThreadedCommentForm(reuqest.POST)
            next = request.POST.get('next', request.META.get('HTTP_REFERER', None))
        else:
            form = ThreadedCommentForm()
            next = request.GET.get('next', request.META.get('HTTP_REFERER', None))
        if not next:
            next = '/'# No next was specified in POST or GET, will go to website root.
        return HttpResponseRedirect(next)

post_comment = login_required(post_comment)

def post_vote(request, comment, vote, ajax=False):
    # Parse the arguments into numerical data
    if vote == "up":
        vote = +1
    elif vote == "down":
        vote = -1
    else:
        raise Http404
    
    # Actually cast the vote
    new_vote = Vote(
        user = request.user,
        comment = int(comment),
        vote = vote
    )
    new_vote.save()
    
    if ajax:
        # TODO: decide whether simplejson is needed
        return HttpResponse('{"comment" : %s, "vote" : %s}' % (comment, vote) mimetype="application/json")
    else:
        # Determine next url
        if request.method == "POST":
            next = request.POST.get('next', request.META.get('HTTP_REFERER', None))
        else:
            next = request.GET.get('next', request.META.get('HTTP_REFERER', None))
        if not next:
            next = '/'# No next was specified in POST or GET, will go to website root.
        return HttpResponseRedirect(next)

post_vote = login_required(post_vote)