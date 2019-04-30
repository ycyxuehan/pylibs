#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""


from .bumblebee import Bumblebee

def run_simple_spider(**kwargs):
    configfile = kwargs.get('config')
    bee = Bumblebee(config=configfile)
    bee.run()