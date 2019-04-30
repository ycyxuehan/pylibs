#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################
# Feature: An easy to use micro service framwork
# Author : Bing
# Version: 0.4.7
# Email  : kun1.huang@outlook.com
# Date   : 2017-06-23
###########################################################
"""

"""
from urllib.parse import parse_qs
from urllib.request import Request
from urllib.request import urlopen
from datetime import datetime
import json
import sys
from multiprocessing import Process
import logging
from time import sleep
from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIServer
from socketserver import ThreadingMixIn

from os import getpid
from os import path as ospath

from .base import SoBase
from .libs import get_process_status
from .libs import gen_random_str
from .libs import kill_process
from .libs import set_daemon
from .libs import write_pid
from .libs import check_soraka
from .libs import get_pid_status

from threading import Thread

class Soraka(SoBase):
    """

    """
    def __init__(self, **kwargs):
        """

        """
        #
        super(Soraka, self).__init__(**kwargs)
        self.__realpath = ospath.split(ospath.realpath(__file__))[0]
        self.host = kwargs.get('host')
        self.port = kwargs.get('port', 30000)
        if self.host is None or self.host == '0.0.0.0':
            self.host = '127.0.0.1'
        location_map = list(kwargs.get('services', []))
        for location in location_map:
            if location.get('args',{}).get('SoAnt'):
                location['handle'] = self.__do_ant
        self.location_map.extend([
            {'location':'/status', 'handle':self.__status, 'method':'GET'},
            {'location':'/status', 'handle':self.__status, 'method':'POST'},
            {'location':'/process', 'handle':self.__process, 'method':'GET'},
            {'location':'/process', 'handle':self.__process, 'method':'POST'},
            {'location':'/monitor', 'handle':self.__monitor, 'method':'GET'},
            {'location':'/kill', 'handle':self.__kill_service, 'method':'GET'},
            {'location':'/service', 'handle':self.__service, 'method':'GET'},
            {'location':'/getservice', 'handle':self.__get_service, 'method':'GET'}
           ])
        #support bootstrap css
        self.add_app(location='/css/bootstrap.min.css', method='GET', handle=self.read_file, args={'filename':ospath.join(self.__realpath, 'css/bootstrap.min.css')})
        self.add_app(location='/css/bootstrap.min.css.map', method='GET', handle=self.read_file, args={'filename':ospath.join(self.__realpath, 'css/bootstrap.min.css.map')})        
        self.add_app(location='/fonts/glyphicons-halflings-regular.ttf', method='GET', handle=self.read_file,
                    args={'filename':ospath.join(self.__realpath, 'fonts/glyphicons-halflings-regular.ttf')})        
        self.add_app(location='/fonts/glyphicons-halflings-regular.woff', method='GET', handle=self.read_file, 
                    args={'filename':ospath.join(self.__realpath, 'fonts/glyphicons-halflings-regular.woff')})        
        self.add_app(location='/fonts/glyphicons-halflings-regular.woff2', method='GET', 
                    handle=self.read_file, args={'filename':ospath.join(self.__realpath, 'fonts/glyphicons-halflings-regular.woff2')})        


        self.add_app()
        self.process_map = {}
        self.status_map = {}
        self.path_key_map = {}
        key = gen_random_str(9)
        self.path_key_map['__service__'] = key
        self.__start_date = datetime.now().strftime('%Y%m%d')
        self.custorm_thread = None
        self.custorm_thread_args = None
    def __status(self, env, resp):
        """
        s
        """
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        pid = params.get('pid')
        method = env.get('REQUEST_METHOD').lower()
        if method == 'get':
            rtype = params.get('type')
            html = json.dumps(self.status_map)
            if pid:
                html = json.dumps(self.status_map.get(str(pid)))
            if rtype == 'html':
                html = self.__get_status_html(pid)
            resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
            yield html.encode()
        if method == 'post':
            try:
                req_body_size = int(env.get('CONTENT_LENGTH'))
                req_body = env.get('wsgi.input').read(req_body_size)
                #eg: '13245':{'234':'2017'} pid:{key:value,key:value}
                jdata = json.loads(req_body.decode())
                self.status_map[pid] = jdata
            except Exception as ex:
                print('soraka.__status:%s' % str(ex))
            resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
            yield 'ok'.encode()

    def __get_status_html(self, pid):
        """

        """
        html = ''
        status_html = ''
        if pid is None:
            pid = getpid()
        with open(ospath.join(self.__realpath, 'html/status.html'), 'r') as template:
            html = template.read()
        if pid:
            status = self.status_map.get(str(pid))
            if status:
                div_tmp = '<div class="row"><div class="col-md-4"><div class="alert alert-info">{KEY}</div></div><div class="col-md-8"><div class="alert alert-success">{VALUE}</div></div></div>'
                #<div class="col-md-4"><div class="alert alert-info">项目</div></div><div class="col-md-8"><div class="alert alert-success">值</div></div>
                keys = sorted(status.keys())
                for key in keys:
                    div = div_tmp.replace('{KEY}', key)
                    value = status.get(key)
                    if 'link' in key.lower():
                        href = value
                        if value[0:1] != '/':
                            href = '/%s' % href
                        value = '<a href="%s">%s</a>' % (href, value)
                    div = div.replace('{VALUE}', str(value))
                    status_html += div
        html = html.replace('{PID}', str(pid))
        html = html.replace('{STATUS}', status_html)
        return html

    def __process(self, env, resp):
        """

        """
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        key = params.get('key')
        name = params.get('name')
        method = env.get('REQUEST_METHOD').lower()
        if method == 'get':
            self.__update_process_status()
            rtype = params.get('type')
            html = json.dumps(self.process_map)
            if key:
                html = json.dumps(self.process_map.get(str(key)))
            if rtype == 'html':
                html = self.__get_process_html(key)
            resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
            yield html.encode()
        elif method == 'post':
            try:
                req_body_size = int(env.get('CONTENT_LENGTH'))
                req_body = env.get('wsgi.input').read(req_body_size)
                #eg: '13245':{'234':'2017'} key:{pid:date,pid:date}
                jdata = json.loads(req_body.decode())
                print(jdata)
                for pid in jdata:
                    print('key', key, 'pid', pid)
                    if self.process_map.get(key) is None:
                        self.process_map[key] = {}
                    self.process_map[key][str(pid)] = {'startdate': jdata.get(pid), 'name':self.__get_app_by_key(key), 'status':'Running'}
            except Exception as ex:
                print('soraka.__process:%s' % str(ex))
            resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
            yield 'ok'.encode()
    def __get_app_by_key(self, key):
        if not key:
            return '__default__'
        for name in self.path_key_map:
            if self.path_key_map.get(name) == key:
                return name
        return '__default__'
    def __get_process_html(self, key):
        html = 'unknow'
        process_html = ''
        if key is None:
            key = ''
        with open(ospath.join(self.__realpath, 'html/process.html'), 'r') as template:
            html = template.read()
        processes = {}
        if key:
            processes = self.process_map.get(str(key))
        else:
            for key in self.process_map:
                for pid in self.process_map.get(key, {}):
                    process = self.process_map.get(key, {}).get(pid)
                    if process:
                        processes[pid] = process
        if processes:
            div_tmp = """<div class="row">
            <div class="col-md-2"><div class="alert alert-info">{PID}</div></div>
            <div class="col-md-2"><div class="alert alert-success">Admin</div></div>
            <div class="col-md-3"><div class="alert alert-success">{STARTDATE}</div></div>
            <div class="col-md-2"><div class="alert alert-success">{STATUS}</div></div>
            <div class="col-md-3"><div class="alert alert-success">
            <a href="{HREFSTATUS}">任务详情</a>|<a href="{HREFMONITOR}">任务资源</a>|<a href={HREFKILL}>中止任务</a></div></div>
            </div>"""
            for pid in processes:
                div = div_tmp.replace('{PID}', str(pid))
                div = div.replace('{STARTDATE}', processes.get(pid, {}).get('startdate'))
                href_status = '/status?pid=%s&type=html' % (str(pid))
                href_monitor = '/monitor?pid=%s&type=html' % (str(pid))                    
                href_kill = '/kill?pid=%s&key=%s' % (str(pid), key)                    
                div = div.replace('{HREFSTATUS}', href_status)
                div = div.replace('{HREFMONITOR}', href_monitor)
                div = div.replace('{HREFKILL}', href_kill)
                status = processes.get(pid, {}).get('status')
                if status == 'Runing':
                    div = div.replace('{STATUS}', '运行中')
                else:
                    div = div.replace('{STATUS}', '已关闭')
                process_html += div
        html = html.replace('{PROCESS}', process_html)
        html = html.replace('{NAME}', self.__get_service_name(key))
        return html
    
    def __update_process_status(self):
        """

        """
        for key in self.process_map:
            for pid in self.process_map.get(key):
                status = get_pid_status(pid)
                if status:
                    self.process_map[key][pid]['status'] = 'Runing'
                else:
                    self.process_map[key][pid]['status'] = 'Closed'

    def __get_service_name(self, key):
        """
        
        """
        if key is None or key == '':
            return ''
        for name in self.path_key_map:
            if self.path_key_map.get(name) == key:
                return name
        return ''

    def __monitor(self, env, resp):
        """

        """
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        pid = params.get('pid')
        rtype = params.get('type')
        status = get_process_status(pid)
        html = json.dumps(status)
        if pid:
            html = json.dumps(status.get(str(pid)))
        if rtype == 'html':
            html = self.__get_monitor_html(status, pid)
        resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
        yield html.encode()
    def __get_monitor_html(self, monitor, pid=''):
        """

        """
        html = ''
        monitor_html = ''
        with open(ospath.join(self.__realpath, 'html/monitor.html'), 'r') as template:
            html = template.read()
        if monitor:
            div_tmp = '<div class="row"><div class="col-md-4"><div class="alert alert-info">{KEY}</div></div><div class="col-md-8"><div class="alert alert-success">{VALUE}</div></div></div>'
            div_tmp_net = '<div class="row"><div class="col-md-2"><div class="alert alert-info">{KEY}</div></div>\
            <div class="col-md-4"><div class="alert alert-success">{SENT}</div></div>\
            <div class="col-md-4"><div class="alert alert-success">{RECV}</div></div></div>'
            #<div class="col-md-4"><div class="alert alert-info">项目</div></div><div class="col-md-8"><div class="alert alert-success">值</div></div>
            div_tmp_pid = '<div class="row"><div class="col-md-4"><div class="alert alert-info">任务{KEY}</div></div>\
            <div class="col-md-4"><div class="alert alert-success">{PKEY}</div></div>\
            <div class="col-md-4"><div class="alert alert-success">{PVALUE}</div></div></div>'

            for key in monitor:
                div = div_tmp.replace('{KEY}', key)
                value = monitor.get(key)
                if key == 'cpu_used':
                    value = '%f%%' % value
                div = div.replace('{VALUE}', str(value))
                if key == 'net':
                    div = ''
                    for net in value:
                        sent =  value.get(net,{}).get('sent')
                        recv =  value.get(net,{}).get('recv')
                        div_net = div_tmp_net.replace('{KEY}', '%s</div></div><div class="col-md-2"><div class="alert alert-info">%s' %(key, net))
                        div_net = div_net.replace('{SENT}', 'Sent(B/s): %s' % str(sent))
                        div_net = div_net.replace('{RECV}', 'Recv(B/s): %s' % str(recv))
                        div += div_net
                elif key == str(pid):
                    div = ''
                    for pkey in value:
                        pvalue =  value.get(pkey)
                        if pkey == 'cpu':
                            pvalue = '%f%%' % pvalue
                        div_pid = div_tmp_pid.replace('{KEY}', key)
                        div_pid = div_pid.replace('{PKEY}', str(pkey))
                        div_pid = div_pid.replace('{PVALUE}', str(pvalue))
                        div += div_pid
                monitor_html += div
        html = html.replace('{PID}', pid)
        html = html.replace('{MONITOR}', monitor_html)
        return html

    def __service(self, env, resp):
        """

        """
        resp_str = 'unknow'
        try:
            query = parse_qs(env.get('QUERY_STRING'))
            params = {key:query[key][0] for key in query}
            key = self.path_key_map.get('__service__')
            if self.process_map.get(key) is None:
                self.process_map[key] = {}
            pid = getpid()
            self.process_map[key][str(pid)] = {'startdate': self.__start_date, 'name':key}
            resp_str = str(self.service(params))
        except Exception as ex:
            print('soraka.__service:%s', str(ex))
            resp_str = json.dumps({'status':'error', 'error':str(ex)})
        resp('200 OK', [('Content-type', 'application/json;charset=utf-8')])
        yield resp_str.encode('utf-8')

    def service(self, params):
        """

        """
        pass

    def __do_ant(self, env, resp):
        """

        """
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        method = env.get('REQUEST_METHOD').lower()
        url_path = str(env.get('PATH_INFO'))
        location = self.get_app(url_path, method)
        name = location.get('name', 'unkown')
        args = env.get('__args__')
        ant = args.get('SoAnt')
        params['__key__'] = self.path_key_map.get(name)
        if params['__key__'] is None:
            params['__key__'] = gen_random_str()
            self.path_key_map[name] = params['__key__']
        if ant is None:
            resp('200 OK', [('Content-type', 'text/plain;charset=utf-8')])
            return 'SoAnt object not found.'.encode('utf-8')
        process = Process(target=ant.run, args=(params,))
        process.start()
        html = self.__get_do_ant_html(params['__key__'])
        resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
        yield html.encode()

    def __get_do_ant_html(self, key):
        """

        """
        html = ''
        href = ''
        with open(ospath.join(self.__realpath, 'html/do_ant.html'), 'r') as template:
            html = template.read()
        if key:
            href = 'http://%s:%s/process?key=%s&type=html' % (self.host, str(self.port), str(key))
        else:
            key = ''
        html = html.replace('{HREF}', href)
        html = html.replace('{KEY}', key)
        return html

    def __kill_service(self, env, resp):
        """

        """
        html="""
        <html>
            <head>
                <meta charset="UTF-8">
                <link rel="icon" href="data:image/ico;base64,aWNv">
            </head>
            <body>
            </body>
            <script type="text/javascript">
                window.location.href = '/process?key={KEY}&type=html'
            </script>	
        </html>

        """
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        pid = params.get('pid')
        key = params.get('key')
        data = str(kill_process(pid))
        resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
        html = html.replace('{KEY}', key)
        yield html.encode()

    def get_class_name(self):
        """

        """
        type_str = str(type(self))
        import re
        class_name = re.findall(r'[A-Z]{1}\w+', type_str)
        if class_name:
            return class_name[0]
        return None

    def __get_service(self, env, resp):
        """

        """
        html = 'unkown'
        query = parse_qs(env.get('QUERY_STRING'))
        params = {key:query[key][0] for key in query}
        name = params.get('name')
        rtype = params.get('type')
        html = json.dumps(self.path_key_map)
        print(html)
        if name:
            html = json.dumps(self.path_key_map.get(str(name)))
        if rtype == 'html':
            if name:
                html = self.__get_service_html({name:self.path_key_map.get(name)})
            else:
                html = self.__get_service_html(self.path_key_map)
        
        resp('200 OK', [('Content-type', 'text/html;charset=utf-8')])
        yield html.encode()

    def __get_service_html(self, services):
        """

        """
        html = ''
        div_tmp = """<div class="row"><div class="col-md-3"><div class="alert alert-info">{NAME}</div></div>
        <div class="col-md-3"><div class="alert alert-success">{ID}</div></div>
        <div class="col-md-3"><div class="alert alert-success">{RUNNER}</div></div>
        <div class="col-md-3"><div class="alert alert-success">
        <a href="/process?key={ID}&type=html">服务详情</a></div></div></div>
        """
        service_html = ''
        with open(ospath.join(self.__realpath, 'html/servicelist.html'), 'r') as template:
            html = template.read()
        for key in services:
            div = div_tmp.replace('{NAME}', key)
            div = div.replace('{ID}', services.get(key))
            if key == '__service__':
                div = div.replace('{RUNNER}', 'System')
            else:
                div = div.replace('{RUNNER}', 'Admin')
            service_html += div
        html = html.replace('{SERVICES}', service_html)
        return html
    def report(self, status):
        pid = status.get('pid')
        self.status_map[pid] = status

    def thread_method(self):
        return True

class SoStdOut(object):
    """

    """
    def __init__(self, key='', pid=''):
        self.key = key
        self.pid = pid
        self.stdout = sys.stdout
    def write(self, msg):
        self.stdout.writelines(msg)
        try:
            pass
        except Exception as ex:
            print(ex)

    def flush(self):
        self.stdout.flush()


class SoAnt(object):
    """

    """
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '0.0.0.0')
        if self.host == '0.0.0.0':
            self.host = '127.0.0.1'
        self.port = kwargs.get('port', 30000)

    def run(self, params):
        """
        
        """
        key = params.get('__key__')
        if key:
            set_daemon()
            self.__add_process(key)
            self.service(params)

    def service(self, params):
        pass

    def report(self, status):
        """

        """
        if isinstance(status, dict):
            try:
                data = json.dumps(status).encode()
                header = {'Content-Length':len(data)}
                url = "http://%s:%s/status?pid=%s" %(self.host, str(self.port), str(getpid()))
                print('report', url)
                req = Request(url=url, headers=header)
                response = urlopen(req, data=data, timeout=3)
                return response
            except Exception as ex:
                print('SoAnt.report:%s' % str(ex))

    def __add_process(self, key):
        """

        """
        try:
            pid = getpid()
            pid_data = {
                str(pid):datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            url = "http://%s:%s/process?key=%s" % (self.host, str(self.port), key)
            print('add process', url)
            urlopen(url=url, data=json.dumps(pid_data).encode(), timeout=3)
        except Exception as ex:
            print('SoAnt.__add_process:%s' % str(ex))

class __MulitSoraka(ThreadingMixIn, WSGIServer):
    pass

def __run(soraka, filename, host, port):
    """

    """
    try:
        set_daemon()
        pid = getpid()
        write_pid(pid, filename)
        #start a custorm thread
        soraka.custorm_thread = Thread(target=soraka.thread_method, args=())
        soraka.custorm_thread.setDaemon(True)
        soraka.custorm_thread.start()
        httpd = make_server(host, int(port), soraka, __MulitSoraka)
        print('serving on %s:%s' % (host, port))
        httpd.serve_forever()
    except Exception as ex:
        print('__run:%s' % str(ex))

def start_server(soraka, host=None, port=None):
    """
        s
    """
    if not soraka:
        return
    #set_daemon()
    class_name = soraka.get_class_name()
    if class_name:
        if host is None:
            host = soraka.host
        if port is None:
            port = soraka.port
        filename = '/tmp/soraka/%s_%s.pid' % (class_name.lower(), str(port))
        process = Process(target=__run, args=(soraka, filename, host, port))
        process.start()
        while True:
            sleep(60)
            if not check_soraka(filename):
                print('soraka is exited, restarting...')
                process = Process(target=__run, args=(soraka, filename, host, port))
                process.start()
