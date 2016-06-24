#!/usr/bin/python
import os
import sys
# import subprocess
# import time
# from multiprocessing import Process, Queue
#
#
# def get_queue():
#     return q

#
# def check():
#     while True:
#         ip = '192.168.0.8'
#         print('Thread: Pinging %s' % (ip))
#         ret = subprocess.call("ping -c 1 %s" % ip,
#             shell=True,
#             stdout=open('/dev/null', 'w'),
#             stderr=subprocess.STDOUT)
#         if ret == 0:
#             #print("%s: is alive" % ip)
#             q.put('%f: %s is alive' % (time.time(), ip))
#         else:
#             #print("%s: did not respond" % ip)
#             q.put('%f: %s is dead' % (time.time(), ip))
#         time.sleep(10)
#
#


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "t3guard.settings")
    from django.core.management import execute_from_command_line

    # q = Queue()
    #
    # p_django = Process(target=execute_from_command_line, args=(sys.argv,))
    execute_from_command_line(sys.argv)
    # p_checker = Process(target=check)
    #
    # p_django.start()
    # p_checker.start()
    #
    # p_django.join()
