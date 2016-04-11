#!/usr/bin/python

import subprocess
import sys

hosts = ['h1','h2','h3','h4','h5','h6','h7','h8','h16']
util_m = '/home/mininet/mininet/util/m'
sched_script = '/home/mininet/Documents/scheduled_start.py'

for host in hosts:
  print "Starting on", host
  subprocess.Popen([util_m, host, sched_script, host, sys.argv[1]])