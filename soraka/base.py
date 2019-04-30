#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################
# Feature: An easy to use micro service framwork
# Author : Bing
# Version: 0.2.1
# Email  : kun1.huang@outlook.com
# Date   : 2017-04-17
###########################################################
"""

"""
from os import path as ospath
from http.server import BaseHTTPRequestHandler
from wsgiref.simple_server import WSGIRequestHandler
_MIME_MAPS={
    'html':'text/html',
    'css':'text/css',
    'js':'application/javascript',
    'json':'application/json',
    'woff':'application/octet-stream',
    'woff2':'application/octet-stream',
    'ttf':'application/x-font-ttf'
}
class SoBase(object):
    """

    """
    def __init__(self, **kwargs):
        """

        """
        self.__realpath = ospath.split(ospath.realpath(__file__))[0]
        self.location_map = kwargs.get('services', [])
        if type(self.location_map) is not type([]):
            self.location_map = []
        self.add_app(location='/favicon.ico', method='GET', handle=self.read_file, args={'filename':'img/favicon.ico'})

    def __call__(self, env, resp):
        """

        """
        url_path = str(env.get('PATH_INFO'))
        method = env.get('REQUEST_METHOD').lower()
        location = self.get_app(url_path, method)
        handler = location.get('handle')
        args = location.get('args')
        env['__args__'] = args
        if handler is None:
            return self.__not_found_404(env, resp)
        return handler(env, resp)

    def get_app(self, path, method):
        """

        """
        for location in self.location_map:
            lpath = location.get('location')
            lmethod = location.get('method').lower()
            if lpath == path and lmethod == method.lower():
                return location
        if '.' in path and method == 'get':
            return {'handle':self.read_file, 'args':{'filename':path[1:]}}
        return {'handle':None}

    def add_app(self, **kwargs):
        """
            add
        """
        handle = kwargs.get('handle')
        path = kwargs.get('location', '/')
        method = kwargs.get('method', 'get')
        args = kwargs.get('args')
        if handle and path and method:
            self.location_map.append(
                {'location':path, 'method':method, 'handle':handle, 'args':args}
            )

    def delete_app(self, path, method='GET'):
        """
            delete
        """
        for location in self.location_map:
            lpath = location.get('location')
            lmethod = location.get('method').lower()
            if lpath == path and lmethod == method.lower():
                self.location_map.remove(location)
    def __not_found_404(self, env, resp):
        """

        """
        resp('404 not found', [('Content-type', 'text/plain')])
        yield 'Not Found'.encode()

    def __favicon(self, env, resp):
        """

        """
        resp('200 OK', [('Content-type', 'text/plain')])
        data = self.__get_icon()
        yield data.encode()
    def __get_icon(self):
        """
            get
        """
        icon = ospath.join(self.__realpath,'img/favicon.ico')
        try:
            if ospath.isfile(icon):
                with open(icon, 'rb') as read:
                    return read.read()
            return 'aaa'
        except Exception as ex:
            print('__get_icon:%s' % str(ex))
            return 'aaaa'
    def read_file(self, env, resp):
        """
            response a file
        """
        args = env.get('__args__', {})
        filename = args.get('filename', 'unknow')
        data = 'unkown'.encode()
        try:
            print('readfile:', filename)
            if ospath.isfile(filename):
                with open(filename, 'rb') as read:
                    data = read.read()
        except Exception as ex:
            data = str(ex).encode()
        
        content_type = _MIME_MAPS.get(filename.split('.')[-1],'text/plain')
        resp('200 OK', [('Content-type', content_type)])
        yield data
    