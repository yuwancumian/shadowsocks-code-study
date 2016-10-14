#!/usr/bin/env python
# coding:utf-8
import os
import time
import signal

print os.getpid()

def handler(signum, frame):
    print "Received {0}".format(signum)

signal.signal(signal.SIGUSR1, handler)
signal.signal(signal.SIGINT, handler)

while 1:
    print "waiting..."
    time.sleep(5)



"""
kill -SIGUSR1 pid

"""
