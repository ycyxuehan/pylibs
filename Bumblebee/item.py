#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

from .parser import HTMLParser

class Item(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.expression = kwargs.get('expression')
        self.parser = kwargs.get('parser')
        self.value = kwargs.get('default')
    def set_value(self, value):
        if value:
            self.value = value
    def show(self):
        print(self.name, ':', self.value)
class ItemCollection(object):
    def __init__(self, **kwargs):
        self.items = []
        item_data = kwargs.get('data')
        self.htmlparser = kwargs.get('htmlparser')
        self.textparser = kwargs.get('textparser')
        self.cols = []
        self.has_item = False
        self.__init_collection(item_data)
    def __init_collection(self, item_data):
        # "item":{
        #     "title":{
        #         "xpath":"",
        #         "parser":""
        #     },
        #     "publish_date":{
        #         "parser":"spider.parser.xpath"
        #     },
        #     "_cols":["title", "publish_data"]

        # }
        if isinstance(item_data, dict) is False:
            return False
        cols = item_data.get('_cols')
        if cols is None or cols == []:
            cols = [key for key in item_data]
            cols.remove('_cols')
            cols = cols.sort()
        self.cols = cols
        for col in cols:
            col_data = item_data.get(col)
            print('col:', col, 'col_data:', col_data)
            expression = col_data.get('expression')
            parser = col_data.get('parser')
            default = col_data.get('default')
            print(expression, parser, default)
            self.items.append(Item(name=col, expression=expression, parser=self.htmlparser.get(parser), default=default))
        self.has_item = True
        return True
    def to_csv(self, cols=None):
        items = self._get_item_list(cols)
        res = []
        for item in items:
            res.append(str(item.value).replace('\t', ''))
        print(res)
        return ','.join(res)

    def to_json(self, cols=None):
        items = self._get_item_list(cols)
        return {item.name:item.value for item in items}

    def to_sql(self, table, cols=None):
        if table is None or table == '':
            return None
        items = self._get_item_list(cols)
        sql_prefix = 'insert into %s (' % table
        sql_cols = []
        sql_values = []
        for item in items:
            sql_cols.append(item.name)
            sql_values.append(str(item.value))
        sql = "%s%s)values('%s')" % (sql_prefix, ','.join(sql_cols), "','".join(sql_values))
        return sql

    def _get_item_list(self, cols):
        cols = self.cols if isinstance(cols, list) is False else cols
        if isinstance(cols, list) is False:
            return self.items
        res = []
        print('cols:', cols)
        for col in cols:
            for item in self.items:
                if item.name == col:
                    res.append(item)
                    break
        return res

    def parse_item(self, html):
        if html is None or html == '':
            return False
        res = []
        for item in self.items:
            value = item.parser(html=html, expression=item.expression)
            item.set_value(value)
            res.append(item)
        self.items = res
        return True
    