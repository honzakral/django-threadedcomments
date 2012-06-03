from core.models import Message
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect


def home(request):
    context = {
        'messages': Message.objects.all(),
    }
    return render_to_response('core/home.html', context, context_instance=RequestContext(request))


@csrf_protect
def message(request, id):
    context = {
        'message': get_object_or_404(Message, pk=id),
    }
    return render_to_response('core/message.html', context, context_instance=RequestContext(request))
