#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################
# Feature: An easy to use micro service framwork
# Author : Bing
# Version: 0.2.1
# Email  : kun1.huang@outlook.com
# Date   : 2017-04-17
###########################################################

from time import sleep
from random import Random
import psutil
from os import path
from os import makedirs

def get_process_status(pid=None):
    cpu = psutil.cpu_percent() #float, 11.1
    mem = psutil.virtual_memory() #object
    result = {}
    result['cpu_used'] = cpu
    result['mem_total'] = mem.total
    result['mem_used'] = mem.used
    result['mem_available'] = mem.available
    result['mem_free'] = mem.free
    result['net'] = get_net_flow()
    if pid:
        pid_exists = psutil.pid_exists(int(pid))
        print(pid_exists)
        if pid_exists:
            process = psutil.Process(pid=int(pid))
            result[str(pid)] = {
                'cpu':process.cpu_percent(),
                'mem':process.memory_percent() * mem.total / 100,
                'running':process.is_running(),
                'status':process.status()
            }
    return result

def get_net_flow(eth=None):
    netold = psutil.net_io_counters(pernic=True)
    result = {}
    if eth and not(eth in netold.keys()):
        return None
    if eth is None:
        sleep(1)
        netnew = psutil.net_io_counters(pernic=True)
        for eth in netold:
            if eth == 'lo':
                continue
            ethdata_old = netold.get(eth)
            ethdata_new = netnew.get(eth)
            sent = ethdata_new.bytes_sent - ethdata_old.bytes_sent
            recv = ethdata_new.bytes_recv - ethdata_old.bytes_recv
            if recv > 1:
                result[eth] = {'sent':sent, 'recv':recv}
        return result
    sleep(1)
    netnew = psutil.net_io_counters(pernic=True)
    ethdata_old = netold.get(eth)
    ethdata_new = netnew.get(eth)
    sent = ethdata_new.bytes_sent - ethdata_old.bytes_sent
    recv = ethdata_new.bytes_recv - ethdata_old.bytes_recv
    result[eth] = {'sent':sent, 'recv':recv}
    return result

def gen_random_str(max=6):
    service_id = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(max):
        service_id += chars[random.randint(0, length)]
    return service_id

def kill_process(pid):
    if psutil.pid_exists(int(pid)):
        try:
            process = psutil.Process(pid=int(pid))
            process.kill()
            return True
        except Exception as ex:
            print(ex)
            return False
    return False

def suspend_process(pid):
    if psutil.pid_exists(int(pid)):
        try:
            process = psutil.Process(pid=int(pid))
            process.suspend()
        except Exception as ex:
            print(ex)

def resume_process(pid):
    if psutil.pid_exists(int(pid)):
        try:
            process = psutil.Process(pid=int(pid))
            process.resume()
        except Exception as ex:
            print(ex)

def set_daemon():
    try:
        import os
        pid = os.fork()
        if pid>0:
            exit(0)
    except Exception as ex:
        print('set daemon error:', ex)

def write_pid(pid, filename):
    if not pid or not filename:
        return False
    ppath = '/'.join(filename.split('/')[:-1])
    if not path.isdir(ppath):
        makedirs(ppath)
    with open(path.join(ppath, filename), 'w') as pidfile:
        pidfile.writelines('%s' % str(pid))

def check_soraka(filename):
    with open(filename) as pidfile:
        pid = pidfile.readline()
        if pid:
            return psutil.pid_exists(int(pid))
    return False

def get_pid_status(pid):
    if not psutil.pid_exists(int(pid)):
        return False
    try:
        process = psutil.Process(pid=int(pid))
        return process.is_running()
    except Exception as ex:
        print(ex)
    return False