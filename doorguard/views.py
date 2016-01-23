from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.safestring import mark_safe

from .models import Device, Log, Config, Temperature, Humidity


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

    temps = Temperature.objects.filter(timestamp__gt=start)
    temp_time = mark_safe([timezone.localtime(t.timestamp).strftime('%Y-%m-%d %H:%M:%S') for t in temps].__str__())
    temp_values = mark_safe([t.value for t in temps].__str__())
    curr_temp = '{0:.1f}'.format(temps.latest('timestamp').value)

    humids = Humidity.objects.filter(timestamp__gt=start)
    humidity_time = mark_safe([timezone.localtime(h.timestamp).strftime('%Y-%m-%d %H:%M:%S') for h in humids].__str__())
    humidity_values = mark_safe([h.value for h in humids].__str__())


#    while start < timezone.now():
#        cnt = Log.objects.filter(log_type__exact='MO', status=True, created__range=[start, start+delta]).count()
#        motion_time.append(start)
#        motion_count.append(cnt)

#        start += delta
#    motion_datestmp = last_motion
#    motion_time = mark_safe([timezone.localtime(m).strftime('%Y-%m-%d %H:%M:%S') for m in motion_time].__str__())
    #motion_state = mark_safe([ int(m.status) for m in last_motions].__str__())
    #motion_time = mark_safe(motion_time.__str__())
#    motion_count = mark_safe(motion_count.__str__())

    return render_to_response(
        'index.html',
        locals()
    )

def temperature_details(request, days=3):
    start = timezone.now() - timezone.timedelta(days=days)
    temps = Temperature.objects.filter(timestamp__gt=start)
    temp_time = mark_safe([timezone.localtime(t.timestamp).strftime('%Y-%m-%d %H:%M:%S') for t in temps].__str__())
    temp_values = mark_safe([t.value for t in temps].__str__())
    
    curr_temp = '{0:.1f}'.format(temps.latest('timestamp').value)
    t = Temperature.objects.filter(timestamp__gt=start)
    temperature_time = mark_safe([timezone.localtime(m).strftime('%Y-%m-%d %H:%M:%S') for m in t].__str__())
    temperature_count = mark_safe(motion_count.__str__())
    return render_to_response(
        'temperatures.html',
        locals()
    )


def humidity_details(request, days=3):
    pass


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
