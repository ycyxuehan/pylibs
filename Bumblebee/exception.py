#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""


class ConfigError(Exception):
    def __init__(self, err_id):
        self.error_map = {

        }
        if isinstance(err_id, int):
            pass