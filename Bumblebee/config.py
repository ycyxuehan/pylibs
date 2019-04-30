#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""


from .scheduler import Scheduler, SON, PARENT
class Configer(object):
    def __init__(self, config_data):
        self.__init_config(config_data)

    def __init_config(self, config_data):
        if config_data:
            scheduler_data = config_data.get('SCHEDULER',{})
            parser_ex = config_data.get('PARSER_EX')
            storage_ex = config_data.get('STORAGE_EX')
            downloader_ex = config_data.get('DOWNLOADER_EX')
            env_data = config_data.get('ENV')
            self.scheduler_list = self.set_scheduler(scheduler_data, downloader_ex, parser_ex, storage_ex, env_data)

    def set_scheduler(self, data, downloader, parser, storage, env):
        res = []
        schedulers = {}
        if isinstance(data, dict) is False:
            return res
        for name in data:
            schedulers[name] = Scheduler(name=name, data=data.get(name), down_ex=downloader, parser_ex=parser, storage_ex=storage, env=env)
            #res.append(Scheduler(name=name, data=data.get(name)))
        schedulers = self.sort_scheduler(schedulers)
        res = [schedulers.get(key) for key in schedulers]
        return res

    def sort_scheduler(self, schedulers):
        for name in schedulers:
            scheduler = schedulers.get(name)
            identity = scheduler.identity
            if identity == SON:
                parent_name = scheduler.parent_name
                pscheduler = schedulers.get(parent_name)
                scheduler.parent = pscheduler
                pscheduler.add_son(scheduler)
        return schedulers

    