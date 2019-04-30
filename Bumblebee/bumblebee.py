#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

from os import path
import json
from .scheduler import Scheduler
from .downloader import DownLoader
from .parser import HTMLParser, TextPaser, URLParser
from .storage import Storage
from .command import get_command
# from .common import analyze_env
from .libs import analyze_env

class Bumblebee(object):
    def __init__(self, **kwargs):
        config_data = kwargs.get('config_data')
        if isinstance(config_data, dict) is False or config_data == {}:
            config = kwargs.get('config')
            print('config:', config)
            config_data = self.load_config(config)
        parser_ex = config_data.get('PARSER_EX')
        storage_ex = config_data.get('STORAGE_EX')
        downloader_ex = config_data.get('DOWNLOADER_EX')
        scheduler_data = config_data.get('SCHEDULER')
        env_data = config_data.get('ENV')
        self.env = self.__init_env(env_data)
        self.env['_DOWNLOADER_'] = self.__init_obj(DownLoader(**kwargs), downloader_ex)
        self.env['_HTMLPARSER_'] = self.__init_obj(HTMLParser(**kwargs), parser_ex)
        self.env['_TEXTPARSER_'] = self.__init_obj(TextPaser(**kwargs), parser_ex)
        self.env['_URLPARSER_'] = self.__init_obj(URLParser(**kwargs), parser_ex)
        self.env['_STORAGE_'] = self.__init_obj(Storage(**kwargs), storage_ex)
        self.scheduler = self.__init_scheduler(scheduler_data)
    def load_config(self, configfile):
        if path.isfile(configfile) is False:
            raise IOError
        config_data = None
        try:
            config_data = json.load(open(configfile))
        except Exception as identifier:
            pass
        return config_data

    def __init_obj(self, obj, data):
        if isinstance(data, dict):
            for pname in data:
                pdata = analyze_env(data.get(pname), self.env)
                obj.add(pname, get_command(pname, pdata))
        return obj
    def __init_env(self, env):
        if isinstance(env, dict) is False:
            return {}
        for key in env:
            env[key] = analyze_env(env.get(key), env)
        return env

    def __init_scheduler(self, scheduler_data):
        if isinstance(scheduler_data, dict):
            for name in scheduler_data:
                data = scheduler_data.get(name,{})
                identity = data.get('identity')
                if identity.upper() == 'ROOT':
                    return Scheduler(data=data, env=self.env, scheduler_data=scheduler_data, name=name)
        return None

    def run(self):
        print('started...')
        if self.scheduler:
            return self.scheduler.schedule()
