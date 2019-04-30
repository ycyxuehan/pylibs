#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

from urllib.request import urlopen
from requests import session
from .libs import get_ua

class DownLoader(object):
    def __init__(self, **kwargs):
        self.downloader_list = {
            'bumblebee.downloader.base':self.wget,
            'bumblebee.downloader.session':self.session_get
        }
    
    def wget(self, url, **kwargs):
        encode = kwargs.get('encoding', "utf-8")
        timeout = kwargs.get('timeout', 3)
        try:
            response = urlopen(url,timeout=timeout)
            data = response.read()
            return data.decode(encode)
        except Exception as identifier:
            print('bumblebee.downloader.base:', identifier)
        return None
    
    def add(self, name, downloader):
        self.downloader_list[name] = downloader

    def get(self, name):
        return self.downloader_list.get(name)

    def session_get(self, url, **kwargs):
        encode = kwargs.get('encoding', "utf-8")
        timeout = kwargs.get('timeout', 1)
        headers = kwargs.get('config')
        if headers.get('User-Agent', '') == '':
            headers['User-Agent'] = get_ua()
        client = session()
        client.headers = headers
        response = client.get(url)
        response.encoding = encode
        return response.text
