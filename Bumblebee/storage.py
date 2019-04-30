#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

from os import path, makedirs
from datetime import datetime
from .item import ItemCollection
class Storage(object):
    def __init__(self, **kwargs):
        self.storage_list = {
            'bumblebee.storage.html':self.html,
            'bumblebee.storage.csv':self.csv,
            'bumblebee.storage.database.mysql':self.mysql,
            'bumblebee.storage.json':self.json
        }
    
    def add(self, name, storage):
        self.storage_list[name] = storage

    def html(self, **kwargs):
        html = kwargs.get('html', '')
        filename = kwargs.get('filename', '')
        destpath = kwargs.get('destpath', './')
        if path.isdir(destpath) is False:
            try:
                makedirs(destpath)
            except Exception as identifier:
                print('bumblebee.storage.html:', identifier)
                return False
        if filename == '':
            url = kwargs.get('url', '')
            if url:
                filename = url.split('/')[-1]
                filename = filename.split('?')[0]
            else:
                filename = datetime.now().strftime('%Y%m%d%H%M%S.html')
        filepath = path.join(destpath, filename)
        with open(filepath, mode='w') as file:
            file.writelines(html)
        return True

    def csv(self, **kwargs):
        item = kwargs.get('items')
        cols = kwargs.get('cols')
        if isinstance(item, ItemCollection) is False:
            return False
        filename = kwargs.get('filename', 'data.csv')
        destpath = kwargs.get('destpath', './')
        if path.isdir(destpath) is False:
            try:
                makedirs(destpath)
            except Exception as identifier:
                print('bumblebee.storage.csv:', identifier)
                return False
        filepath = path.join(destpath, filename)
        with open(filepath, mode='a') as file:
            file.writelines('%s\n' % str(item.to_csv(cols)))
        return True
    def mysql(self, **kwargs):
        items = kwargs.get('items')
        dbconnstr = kwargs.get('dbconnectstr')


    def json(self, **kwargs):
        pass

    def _default(self, **kwargs):
        print('storage nothing')
    def get(self, name):
        return self.storage_list.get(name, self._default)