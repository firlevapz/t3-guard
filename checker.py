#!/usr/bin/python3
import os
import subprocess
import time
import threading
import RPi.GPIO as GPIO

import django
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doorguard.settings")
from doorguard.models import Device, Log, Config
django.setup()

check_pin = 7   # GPIO-Pin nr to check on raspi

config_reload = 10 # seconds how often reload the config

device_check_wait = 10*60  # each 10 minutes check for devices
ping_retry = 3   # how often try to ping device before set inactive
door_check_wait = 1 # check door every 2 seconds
alarm_delay = 10 # seconds to delay alarm from opening the door

pipe_name = '/tmp/doorguard_dhcp_pipe'

stop_threads = threading.Event()    # threading event to stop all threads


def check_devices():
    while not stop_threads.isSet():
        devices = Device.objects.all()  # get all current devices
        for d in devices:
            for i in range(int(ping_retry)):
                ret = subprocess.call("ping -c 1 %s" % d.ip,
                    shell=True,
                    stdout=open('/dev/null', 'w'),
                    stderr=subprocess.STDOUT)
                if ret == 0:
                    break # break retries, if device is alive
                time.sleep(1)
            is_home = (ret == 0)
            if not d.is_home == is_home:
                d.is_home = is_home
                d.save()
                l = Log(device=d, status=is_home, log_type='DE', text='(checker)')
                l.save()
        time.sleep(device_check_wait)


def trigger_alarm():
    # Alarm delay then check again
    time.sleep(alarm_delay)
    # Check again if someone is home now
    if Device.objects.filter(is_home=True).count() > 0:
        return # cancel alarm

    l = Log(log_type='AL')
    l.save()

    try:
        Config.objects.get(config_type='ALARM', name='email', enabled=True)
        for c in Config.objects.filter(config_type='EMAIL', enabled=True):
            send_mail(
                'Doorguard ALARM',
                'Alarm Triggered!!!',
                settings.DEFAULT_FROM_EMAIL,
                [c.name],
                fail_silently=True
            )
    except ObjectDoesNotExist:
        pass # email sending disabled

    try:
        Config.objects.get(config_type='ALARM', name='sound', enabled=True)
        # do some crazy shitty sound action!!!
    except ObjectDoesNotExist:
        pass # sound action disabled


def check_door():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(check_pin, GPIO.IN)
    old_state = GPIO.input(check_pin)

    while not stop_threads.isSet():
        curr_state = GPIO.input(check_pin)
        if old_state != curr_state:
            # state of pin changed
            old_state = curr_state
            l = Log(status=curr_state, log_type='DO')
            l.save()

            if curr_state == 0 and Device.objects.filter(is_home=True).count() == 0:
                # Door opened and nobody at home!
                alarm_thread = threading.Thread(target=trigger_alarm)
                alarm_thread.daemon = True
                alarm_thread.start()

            Device.objects.filter(is_home=True).order_by('-modified')

        time.sleep(door_check_wait)


def dhcp_pipe_reader():
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)

    while not stop_threads.isSet():
        with open(pipe_name, 'r') as pipe:
            line = pipe.readline()[:-1]   # get line except \n at end
            line = line.split(' ')        # split up by ' ' in chunks
            cmd = line[0]
            if cmd == 'old' or cmd == 'add':
                mac = line[1]
                ip = line[2]
                hostname = line[3]

                try:
                    d = Device.objects.get(ip=ip, is_home=False)
                    d.is_home = True
                    d.save()
                    l = Log(device=d, status=True, log_type='DE', text='(dhcp)')
                    l.save()
                except ObjectDoesNotExist:
                    pass


if __name__ == '__main__':
    device_thread = threading.Thread(target=check_devices)
    device_thread.daemon = True
    device_thread.start()

    door_thread = threading.Thread(target=check_door)
    door_thread.daemon = True
    door_thread.start()

    dhcp_thread = threading.Thread(target=dhcp_pipe_reader)
    dhcp_thread.daemon = True
    dhcp_thread.start()

    # print('Checker started...')
    # print('Press <Ctrl+C> to end')

    try:
        while True:
            # Load configuration-settings from DB
            for c in Config.objects.filter(config_type='CHECKER', enabled=True):
                locals()[c.name] = float(c.value)
            time.sleep(config_reload)
    except (KeyboardInterrupt, SystemExit):
        print('Interrupt received, cleaning up...')

    try:
        os.unlink(pipe_name)
    except:
        pass

    GPIO.cleanup()
    # print('Cleanup finished')
