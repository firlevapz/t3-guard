#!/usr/bin/python3
import os
import sys
import django


if __name__ == '__main__' and len(sys.argv) > 2:
    cmd = sys.argv[1]
    if cmd == 'old' or cmd == 'add':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doorguard.settings")
        from doorguard.models import Device, Log
        django.setup()

        mac = sys.argv[2]
        ip = sys.argv[3]
        hostname = sys.argv[4]

        try:
            d = Device.objects.get(ip=ip, is_home=False)
            d.is_home = True
            d.save()
            l = Log(device=d, status=True, log_type='DE', text='(dhcp)')
            l.save()
        except DoesNotExist:
            pass
