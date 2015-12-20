from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.safestring import mark_safe

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

    start = timezone.now() - timezone.timedelta(days=1)
    motion_time = []
    motion_count = []
    delta = timezone.timedelta(minutes=15)

    while start < timezone.now():
        cnt = Log.objects.filter(log_type__exact='MO', status=True, created__range=[start, start+delta]).count()
        motion_time.append(start)
        motion_count.append(cnt)

        start += delta
#    motion_datestmp = last_motion
    motion_time = mark_safe([timezone.localtime(m).strftime('%Y-%m-%d %H:%M:%S') for m in motion_time].__str__())
    #motion_state = mark_safe([ int(m.status) for m in last_motions].__str__())
    #motion_time = mark_safe(motion_time.__str__())
    motion_count = mark_safe(motion_count.__str__())

    return render_to_response(
        'index.html',
        locals()
    )


def motion_details(request, days=3):
    devices = Device.objects.all()

    minutes = 10

    start = timezone.now() - timezone.timedelta(days=days)
    motion_time = []
    motion_count = []
    delta = timezone.timedelta(minutes=minutes)

    while start < timezone.now():
        cnt = Log.objects.filter(log_type__exact='MO', status=True, created__range=[start, start+delta]).count()
        motion_time.append(start)
        motion_count.append(cnt)

        start += delta
#    motion_datestmp = last_motion
    motion_time = mark_safe([timezone.localtime(m).strftime('%Y-%m-%d %H:%M:%S') for m in motion_time].__str__())
    #motion_state = mark_safe([ int(m.status) for m in last_motions].__str__())
    #motion_time = mark_safe(motion_time.__str__())
    motion_count = mark_safe(motion_count.__str__())

    range_start = mark_safe(timezone.localtime(timezone.now()-timezone.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'))
    range_end = mark_safe(timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S'))

    return render_to_response(
        'motions.html',
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
