from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect
from .models import Message


def home(request):
    context = {
        'messages': Message.objects.all(),
    }
    return render(request, 'core/home.html', context)


@csrf_protect
def message(request, id):
    context = {
        'message': get_object_or_404(Message, pk=id),
    }
    return render(request, 'core/message.html', context)
