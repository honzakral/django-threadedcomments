from django.http import HttpResponse, HttpResponseRedirect, Http404
from forms import ThreadedCommentForm, VoteForm

def post_comment(request):
    if request.method == "POST":
        form = ThreadedCommentForm(reuqest.POST)
        next = request.POST.get('next', request.META.get('HTTP_REFERER', None))
    else:
        form = ThreadedCommentForm()
        next = request.GET.get('next', request.META.get('HTTP_REFERER', None))
    if not next:
        next = '/'# No next was specified in POST or GET, will go to website root.
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META['REMOTE_ADDR']
        new_comment.save()
        return HttpResponseRedirect(next)
    raise Http404