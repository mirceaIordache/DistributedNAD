#!/usr/bin/python

import subprocess

hosts = ['h15','h12','h11','h14','h13','h10','h9']
switches = ['s1','s2','s3','s4','s5','s6','s7']

util_m = '/home/mininet/mininet/util/m'
dnads_main = '/home/mininet/Documents/DNADS/main.py'

for host, switch in zip(hosts, switches):
    subprocess.Popen([util_m, host, 'python' ,dnads_main, '/home/mininet/Documents/DNADS/inis/{0}.ini'.format(switch)], stdout=open("logs/{0}.log".format(switch), "w"))