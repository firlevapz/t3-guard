#!/usr/bin/python3
import os
import subprocess
import time
import threading
import django
import RPi.GPIO as GPIO

check_pin = 7   # GPIO-Pin nr to check on raspi

device_wait = 10*60  # each 10 minutes check for devices
ping_retry = 3   # how often try to ping device before set inactive
door_wait = 2 # check door every 2 seconds

stop_threads = threading.Event()    # threading event to stop all threads

def check_devices():
    devices = Device.objects.all()  # get all current devices, but only at first run!
    while not stop_threads.isSet():
        for d in devices:
            for i in range(ping_retry):
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
        time.sleep(device_wait)


def check_door():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(check_pin, GPIO.IN)
    old_state = GPIO.input(check_pin)
    states = ['open', 'closed']

    while not stop_threads.isSet():
        curr_state = GPIO.input(check_pin)
        if old_state != curr_state:
            # state of pin changed
            old_state = curr_state
            l = Log(status=curr_state, log_type='DO')
            l.save()

            if curr_state == 0 and Device.objects.filter(is_home=True).count() == 0:
                # Door opened and nobody at home!
                l = Log(log_type='AL')
                l.save()
                #print('ALAAARM')

        time.sleep(door_wait)


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doorguard.settings")
    from doorguard.models import Device, Log
    django.setup()

    device_thread = threading.Thread(target=check_devices)
    device_thread.daemon = True
    device_thread.start()

    door_thread = threading.Thread(target=check_door)
    door_thread.daemon = True
    door_thread.start()

    print('Checker started...')
    input('press <Enter> to stop checker')

    print('Waiting for checker-threads to finish...')
    stop_threads.set()
    GPIO.cleanup()

    if device_thread.is_alive():
        device_thread.join()
    if door_thread.is_alive():
        door_thread.join()

    print('Everything finished nicely')

#     try:
#     sleeper()
# except KeyboardInterrupt:
#     print('\n\nKeyboard exception received. Exiting.')
#     exit()
