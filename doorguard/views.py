from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Device, Log

def index(request):
    last_logs = Log.objects.filter(log_type__exact='DE')[:10]
    last_door_opened = Log.objects.filter(log_type__exact='DO', status=False)[:10]
    devices = Device.objects.all()
    return render_to_response(
        'index.html',
        {
            'devices': devices,
            'last_logs': last_logs,
            'last_door_opened': last_door_opened
        }
    )

