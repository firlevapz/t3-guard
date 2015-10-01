from django.shortcuts import render_to_response
from django.http import HttpResponse


def index(request):
    return render_to_response('index.html')


def add_device(request):
    return render_to_response(
        'add_device.html',
        {'ip': request.META['REMOTE_ADDR']}
    )
