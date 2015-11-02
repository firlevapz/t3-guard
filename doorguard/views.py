from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Device, Log, Config

def index(request):
    last_logs = Log.objects.filter(log_type__exact='DE')[:10]
    last_door_opened = Log.objects.filter(log_type__exact='DO', status=False)[:10]
    devices = Device.objects.all()
    try:
        email_alarm = True if Config.objects.get(config_type='ALARM', name='email', enabled=True) else False
    except Config.DoesNotExist:
        email_alarm = False

    try:
        sound_alarm = True if Config.objects.get(config_type='ALARM', name='sound', enabled=True) else False
    except Config.DoesNotExist:
        sound_alarm = False

    return render_to_response(
        'index.html',
        locals()
    )


@login_required
def toggle_alarm(request, alarm_name):
    try:
        c = Config.objects.get(config_type='ALARM', name=alarm_name)
        c.enabled = not c.enabled
        c.save()
        return HttpResponse('{} set to {}'.format(alarm_name, c.enabled))
    except Config.DoesNotExist:
        return HttpResponse('failed to set {}'.format(alarm_name))
