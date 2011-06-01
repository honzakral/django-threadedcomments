from core.models import Message
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf

def home(request):
    data = dict(messages = Message.objects.all())
    return render_to_response('core/home.html', data)

@csrf_protect
def message(request, id):
    data = dict(message = Message.objects.get(id=id))
    data.update(csrf(request))
    return render_to_response('core/message.html', data)