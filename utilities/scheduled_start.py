#!/usr/bin/python

import time
import threading
import sys
import subprocess
import os

def f():
    subprocess.call(["tcpreplay", "-i", "{0}-eth0".format(sys.argv[1]),  sys.argv[2]])#, stdout=open(os.devnull, "w"))

ts = int(time.time())
remaining = 60 - ts % 60 

t = threading.Timer(remaining, f)
t.start()
t.join()
