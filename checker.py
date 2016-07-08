#!/usr/bin/python
import os
import subprocess
import time
import threading
import RPi.GPIO as GPIO

import django
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "t3guard.settings")
django.setup()
from t3guard.models import Device, Log, Config, Temperature

# check_pin = 7   # GPIO-Pin nr to check on raspi
motion_pin = 11 # GPIO-Pin for motion detection
# temp_pin = 12 # GPIO-Pin for temperature sensor
alarm_pin = 15 # GPIO-Pin for triggerin alarm
# temp_wait = 300 # time interval to record temperature
config_reload = 10 # seconds how often reload the config

device_check_wait = 10*60  # each 10 minutes check for devices
ping_retry = 3   # how often try to ping device before set inactive
# check_wait = 1 # check door every 2 seconds
alarm_delay = 20 # seconds to delay alarm from opening the door
alarm_time = 5 # seconds how long alarm will sound
motion_check_wait = 3 # check door every 2 seconds
radio_wait = 2  # wait n seconds to react on radio states

pipe_name = '/tmp/t3guard_dhcp_pipe'

stop_threads = threading.Event()    # threading event to stop all threads

GPIO.setmode(GPIO.BOARD) # set mode for accessing GPIO pins

GPIO.setup(alarm_pin, GPIO.OUT)
GPIO.output(alarm_pin, 1) # disable alarm in the beginning...


def radio_control():
    """Controls state of the radio, including timing function"""
    while not stop_threads.isSet():
        conf_dict = {a['name']: a for a in Config.objects.filter(
            config_type='RADIO').values('name','enabled','value')}

        if conf_dict['power']['enabled']:
            print('radio power on')
            # power on

        if conf_dict['timer']['enabled']:
            print('timer on')
            # Check if time is not up yet, then power on, otherwise off

        if conf_dict['autoplay']['enabled']:
            print('autoplay on')
            # Check if something is running, then set power

        time.sleep(radio_wait)


def check_devices():
    """Checks which devices are at home"""
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
    """Sends alarm signal (either e-mail or siren)"""
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
        GPIO.output(alarm_pin, 0) # start alarm...
        # just for some seconds to timestamp
        time.sleep(alarm_time)
        GPIO.output(alarm_pin, 1) # disable alarm
    except ObjectDoesNotExist:
        pass # sound action disabled


def check_door():
    """Checks the door-state with magnetic switch"""
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

            if curr_state == 0:
                try:
                    c = Config.objects.get(config_type='ALARM', name='siren_test', enabled=True)
                    c.save()
                    GPIO.output(alarm_pin, 0) # start alarm...
                    # just for some seconds to timestamp
                    if c.value:
                        time.sleep(float(c.value))
                    else:
                        time.sleep(alarm_time)
                    GPIO.output(alarm_pin, 1) # disable alarm
                    c.enabled=False
                    c.save()
                except ObjectDoesNotExist:
                    pass # do nothing

#            Device.objects.filter(is_home=True).order_by('-modified')
        time.sleep(door_check_wait)


def check_motion():
    """Checks motions in the room with IR-detector"""
    GPIO.setup(motion_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while not stop_threads.isSet():
        curr_state = GPIO.input(motion_pin)
        if curr_state:
            l = Log(status=curr_state, log_type='MO')
            l.save()

#           could trigger also alarm here if no phone is present
#            if curr_state == 0 and Device.objects.filter(is_home=True).count() == 0:
                # Door opened and nobody at home!
#                alarm_thread = threading.Thread(target=trigger_alarm)
#                alarm_thread.daemon = True
#                alarm_thread.start()

 #           Device.objects.filter(is_home=True).order_by('-modified')

        time.sleep(motion_check_wait)


def log_temp():
    """Measure temperature and humidity"""
    import Adafruit_DHT
    GPIO.setup(temp_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while not stop_threads.isSet():
        # hard coded nr 18 because of other numbering in Adafruit
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 18)
        t = Temperature(value=temperature)
        t.save()

        time.sleep(temp_wait)


def dhcp_pipe_reader():
    """Checks for new DHCP-registration of devices"""
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

                d, created = Device.objects.get_or_create(mac=mac)
                if created:
                    d.ip = ip
                    d.name = hostname
                    d.save()
                elif d.authorized:
                    d.is_home = True
                    d.save()
                    l = Log(device=d, status=True, log_type='DE', text='(dhcp)')
                    l.save()


if __name__ == '__main__':
    # Start different threads
    device_thread = threading.Thread(target=check_devices)
    device_thread.daemon = True
    device_thread.start()

    radio_thread = threading.Thread(target=radio_control)
    radio_thread.daemon = True
    radio_thread.start()

    # door_thread = threading.Thread(target=check_door)
    # door_thread.daemon = True
    # door_thread.start()

    dhcp_thread = threading.Thread(target=dhcp_pipe_reader)
    dhcp_thread.daemon = True
    dhcp_thread.start()

    #motion_thread = threading.Thread(target=check_motion)
    #motion_thread.daemon = True
    #motion_thread.start()

    # temp_thread = threading.Thread(target=log_temp)
    # temp_thread.daemon = True
    # temp_thread.start()

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
        print('failed to remove pipe')

    GPIO.cleanup()
    # print('Cleanup finished')
