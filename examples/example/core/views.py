from core.models import Message
from django.shortcuts import render_to_response
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
        'message': Message.objects.get(id=id),
    }
    return render_to_response('core/message.html', context, context_instance=RequestContext(request))
