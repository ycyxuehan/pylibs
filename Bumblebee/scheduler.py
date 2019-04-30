#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

import re

from .item import ItemCollection
from .libs import analyze_env
from .libs import list2str
SON = 'son'
PARENT = 'parent'

class Scheduler(object):    
    def __init__(self, **kwargs):
        self.son_list = []
        self.name = kwargs.get('name')
        sdata = kwargs.get('data')
        env = kwargs.get('env')
        self.env = env
        self.origin = analyze_env(sdata.get('origin'), self.env)
        self.identity = sdata.get('identity')
        self.downloader_config = sdata.get('downloader_config')
        self.downloader = self.env.get('_DOWNLOADER_').get(sdata.get('downloader'))
        self.htmlparser = sdata.get('parser')
        self.expression = sdata.get('expression')
        html_storage = sdata.get('storage', {}).get('html')
        result_storage = sdata.get('storage', {}).get('result')
        self.html_storage = self.env.get('_STORAGE_').get(html_storage)
        self.result_storage = self.env.get('_STORAGE_').get(result_storage)
        self.items = ItemCollection(data=sdata.get('item'), htmlparser=self.env.get('_HTMLPARSER_'), textparser=self.env.get('_TEXTPARSER_'))
        self.result_data = sdata.get('result')
        self.scheduler_data = kwargs.get('scheduler_data')
    def schedule(self):
        print('aaaaaaaaaaaaa')
        origins = self.parse_url(self.origin, env=self.env.copy())
        for origin in origins:
            print('exec %s' % origin)
            html = self.downloader(url=origin, config=self.downloader_config)
            self.html_storage(html=html, url=origin)
            env = self.env.copy()
            if self.htmlparser:
                result = self.env.get('_HTMLPARSER_').parse(html, self.expression, env=self.env.copy(), parser=self.htmlparser)
                name = [key for key in self.result_data.keys()][0]
                exp = self.result_data.get(name)
                value = []
                if exp == '$_RESULT':
                    value = result
                else:
                    result = list2str(result)
                    env['_RESULT'] = result
                    exp = analyze_env(exp, env)
                    value = self.env['_TEXTPARSER_'].parse(result, exp, env=env)
                print('value:', value)
                if env.get('_RESULT_') is None:
                    env['_RESULT_'] = {}
                env['_RESULT_'][name] = value
            if self.items.has_item is True:
                for item in self.items.items:
                    item.set_value(list2str(item.parser(html, item.expression)))
                    item.show()
            if self.result_storage:
                self.result_storage(items=self.items, cols=self.items.cols)
            sons = self.get_sons(env, self.scheduler_data.copy())
            for son in sons:
                print('schedule:', son.name)
                yield son.schedule()
        
    def parse_url(self, urls, **kwargs):
        if isinstance(urls, list) is False:
            urls = [urls]
        res = []
        for url in urls:
            expressions = re.findall(r'\[[a-zA-Z0-9_:\.\*\?\^\\\$\+@\-\{\}\[\],\|]+\]', url)
            if expressions and expressions[0]:
                res.extend(self.env.get('_URLPARSER_').parse(url, expressions[0], **kwargs))
        return res if res else urls

    def get_sons(self, env, scheduler_data):
        result = []
        if isinstance(scheduler_data, dict) is False:
            return result
        for name in scheduler_data:
            data = scheduler_data.get(name)
            identity = data.get('identity')
            parent = data.get('parent')
            if identity.upper() == 'SON' and parent == self.name:
                #scheduler_data.pop(name)
                result.append(Scheduler(data=data, scheduler_data=scheduler_data, name=name, env=env))
        return result
