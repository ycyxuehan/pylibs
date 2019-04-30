#!/usr/bin/python3
"""
Name    : Downloader
Version : 0.0.1
Author  : Bing
Email   : kun1.huang@outlook.com
Date    : 2017-11-14
"""

import re
from lxml.etree import HTML

class BaseParser(object):
    def __init__(self, **kwargs):
        self.parser_list = {}
        
    def add(self, name, parser):
        self.parser_list[name] = parser

    def del_parser(self, name):
        self.parser_list.pop(name)

    def modify_parser(self, name, new):
        self.parser_list[name] = new

    def get(self, name):
        result = self.parser_list.get(name) if self.parser_list.get(name) else self.__default
        return result

    def __default(self, text, exp, **kwargs):
        return None

    def parse(self, text, exp, **kwargs):
        if exp and text:
            if isinstance(text, list):
                res = []
                for t in text:
                    r = self.parse(t, exp, **kwargs)
                    if r:
                        res.append(r)
                return res
            exp = exp[1:-1].split(':')
            name = exp[0]
            print('use parser:', name, 'exp:', exp)
            return self.get(name)(text, exp[1:], **kwargs)
        return text

class TextPaser(BaseParser):
    def __init__(self, **kwargs):
        super(TextPaser, self).__init__(**kwargs)
        self.add('regex', self.regex)
        self.add('in', self.in_)
        self.add('!in', self.not_in)
        self.add('prefix', self.prefix)
        self.add('surfix', self.surfix)
        self.add('replace', self.replace)
        self.add('substr', self.substr)
        self.add('range', self.range_)

    def regex(self, text, exp, **kwargs):
        print('regex exp:', exp)
        res = re.findall(exp[0], text)
        return res

    def in_(self, text, exp, **kwargs):
        if text in exp:
            return text
        return None

    def not_in(self, text, exp, **kwargs):
        if text not in exp:
            return text
        return None

    def prefix(self, text, exp, **kwargs):
        return ''.join([exp[0],text])

    def surfix(self, text, exp, **kwargs):
        return ''.join([text, exp[0]])

    def replace(self, text, exp, **kwargs):
        src = exp[0]
        dest = exp[1]
        return str(text).replace(src, dest)

    def substr(self, text, exp, **kwargs):
        return text[int(exp[0]), int(exp[1])]

    def parse(self, text, exp, **kwargs):
        return super(TextPaser, self).parse(text, exp, **kwargs)

    def range_(self, text, exp, **kwargs):
        print(exp)
        rmin = int(exp[0])
        rmax = int(exp[1])
        step = int(exp[2]) if len(exp)>2 else 1
        print(rmin, rmax, step)
        return list(range(rmin, rmax, step))


class URLParser(BaseParser):
    def __init__(self, **kwargs):
        super(URLParser, self).__init__(**kwargs)
        self.add('range', self.range_)
        self.add('list', self.list_)
        self.add('_RESULT_', self.result)

    def range_(self, text, exp, **kwargs):
        rmin = exp[0]
        rmax = exp[1]
        step = exp[2] if len(exp)>2 else 1
        return list(range(rmin, rmax, step))

    def list_(self, text, exp, **kwargs):
        return exp
        
    def result(self, text, exp, **kwargs):
        env = kwargs.get('env', {})
        result_data = env.get('_RESULT_', {})
        print('result_data:', result_data, 'exp:', exp)

        data = result_data.get(exp[0], '')
        if isinstance(data, list) is False:
            data = [data]
        return data
    
    def parse(self, text, exp, **kwargs):
        res = super(URLParser, self).parse(text, exp, **kwargs)
        result = []
        for value in res:
            result.append(text.replace(exp, str(value)))
        result = result if result else None
        return result

class HTMLParser(BaseParser):
    def __init__(self, **kwargs):
        super(HTMLParser, self).__init__(**kwargs)
        self.add('bumblebee.parser.xpath', self.xpath)
        self.textparser = TextPaser(**kwargs)
    def xpath(self, text, exp, **kwargs):
        xpath = exp.get('element')
        print('xpath:', xpath)
        expression = exp.get('value')
        html_obj = HTML(text)
        res = html_obj.xpath(xpath)
        return self.textparser.parse(res, expression, **kwargs)

    def get(self, name):
        result = self.parser_list.get(name) if name else None
        return result

    def parse(self, text, exp, **kwargs):
        parser = kwargs.get('parser')
        if exp and text and isinstance(text, str):
            return self.parser_list.get(parser)(text, exp, **kwargs)
        return ''
    