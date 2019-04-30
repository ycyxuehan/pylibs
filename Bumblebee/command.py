#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

class Cmd(object):
    def __init__(self, **kwargs):
        pass

    def run(self):
        pass


class Python(object):
    def __init__(self, **kwargs):
        pass

    def run(self):
        pass

COMMAND_MAP={
    'bumblebee.cmd':Cmd,
    'bumblebee.python':Python
}
def get_command(name, value):
    if name and value:
        values = value.split(':')
        object_type = values[0]
        return COMMAND_MAP.get(object_type)(name=name, args=values[1:])
    return None