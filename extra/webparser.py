#!/usr/bin/env python
# encoding: utf-8
"""
webparser.py

Created by  on 2012-01-09.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import time
import config
import tagparser
import hashlib

def isTime(tm):
    try:
        ret = time.mktime(time.strptime(tm, config.ISOTIMEFORMAT))
        return True
    except Exception, e:
        return False

class Book_Parser(tagparser.TagParser):
    """docstring for Book_Parser"""
    beginPage = '' #设置遇到设定标志就开始处理
    endPage = '' #设置遇到设定标志就停止处理
    base_url = '' #网站地址
    ignore_list = [] #忽略字段列表
    book_list = [] #小说列表
    last_content_url = '' #最后更新
    host_name = '' #网站名称
    is_origin = False #是否原创

    def __init__(self, dict_key):
        super(Book_Parser, self).__init__()
        if (config.WEB_HOSTS.has_key(dict_key)):
            if (config.WEB_HOSTS[dict_key].has_key('page_start')):
                self.beginPage = config.WEB_HOSTS[dict_key]['page_start']
            if (config.WEB_HOSTS[dict_key].has_key('page_stop')):
                self.endPage = config.WEB_HOSTS[dict_key]['page_stop']
            if (config.WEB_HOSTS[dict_key].has_key('code')):
                self.html_encoding = config.WEB_HOSTS[dict_key]['code']
            if (config.WEB_HOSTS[dict_key].has_key('host')):
                self.base_url = config.WEB_HOSTS[dict_key]['host']
            if (config.WEB_HOSTS[dict_key].has_key('name')):
                self.host_name = config.WEB_HOSTS[dict_key]['name']
            if (config.WEB_HOSTS[dict_key].has_key('is_origin')):
                self.is_origin = config.WEB_HOSTS[dict_key]['is_origin']
            if (config.SYS_ENCODING):
                self.encoding = config.SYS_ENCODING
            else:
                self.encoding = 'UTF-8'
            if (config.SYS_OUT_ENCODING):
                self.out_encoding = config.SYS_OUT_ENCODING
            else:
                self.out_encoding = 'UTF-8'
            self.book_list = []
        else:
            raise Exception('无此网站配置')

    def md5(self):
        if self.htmlData:
            return hashlib.md5(self.htmlData).hexdigest()
        else:
            return None

    def fetchString(self, html=''):
        if html:
            if (self.html_encoding and self.encoding and (self.html_encoding != self.encoding)):
                self.htmlData = html.decode(self.html_encoding, 'ignore').encode(self.encoding, 'ignore')
            else:
                self.htmlData = html
            if (self.beginPage and self.endPage):
                pos_begin = self.htmlData.find(self.beginPage)
                pos_end = self.htmlData.find(self.endPage)
                if ((pos_begin>=0) and (pos_end>pos_begin)):
                    self.htmlData =self.htmlData[pos_begin + len(self.beginPage):pos_end]
            if not self.beginTag:
                self.mainBegin = True
            #bt = time.time()
            self.doParser()
            #print 'parser use time: ' ,time.time() - bt 

    def parser_func(self, num, i):
        return None, None

    def parserBook(self):
        if(len(self.contentList)>0):
            #print len(self.contentList)
            j = 0
            book = {}
            for i in range(0, len(self.contentList)):
                if(0==j%self.field_num):
                    if(book):
                        if(book.has_key('Update_Time') and isTime(book['Update_Time'])):
                            self.book_list.append(book)
                        else:
                            break
                    book = {}
                if(self.contentList[i].lower() in self.ignore_list):
                    j -= 1
                else:
                    key, value = self.parser_func(j%self.field_num, i)
                    if (key):
                        book[key] = value
                        #print j, i, key, value.decode(self.encoding)
                j += 1

            if(book):
                if(book.has_key('Update_Time') and isTime(book['Update_Time'])):
                    self.book_list.append(book)
        #for b in self.book_list:
            #print b['Name'].decode(self.html_encoding, 'ignore').encode(self.out_encoding, 'ignore')
        #print len(self.book_list)


class Qidian_Parser(Book_Parser):
    """起点解析"""
    field_num = 16
    ignore_list = ['[vip]']

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                8: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                9: lambda: ['Name', self.contentList[i]], 
                10: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                11: lambda: ['Content', self.contentList[i]], 
                12: lambda: ['Chars', self.contentList[i]], 
                13: lambda: ['Author_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                14: lambda: ['Author', self.contentList[i]], 
                15: lambda: ['Update_Time', '20' + self.contentList[i] + ':00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Skxsw_Parser(Book_Parser):
    """搜客小说网解析"""
    field_num = 8
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                2: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Content', self.contentList[i]], 
                4: lambda: ['Author', self.contentList[i]], 
                5: lambda: ['Chars', self.contentList[i]], 
                6: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value

class Dukankan_Parser(Book_Parser):
    """读看看解析"""
    field_num = 12
    ignore_list = []

    def parser_func(self, num, i):
        year = time.strftime('%Y', time.localtime())
        key = None
        value = None
        try:
            key, value = {
                4: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Name', self.contentList[i]], 
                6: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                7: lambda: ['Content', self.contentList[i]], 
                8: lambda: ['Author_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                9: lambda: ['Author', self.contentList[i]], 
                10: lambda: ['Update_Time', year + '-' + 
                             self.contentList[i].replace('月', '-').replace('日', '')
                             + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Wjskw_Parser(Book_Parser):
    """万卷书库解析"""
    field_num = 8
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                1: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                2: lambda: ['Name', self.contentList[i]], 
                3: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                4: lambda: ['Content', self.contentList[i]], 
                5: lambda: ['Author_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                6: lambda: ['Author', self.contentList[i]], 
                7: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Sj53_Parser(Book_Parser):
    """53书居解析"""
    field_num = 8
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                2: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Content', self.contentList[i]], 
                4: lambda: ['Author', self.contentList[i]], 
                5: lambda: ['Chars', self.contentList[i]], 
                6: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Zw93_Parser(Book_Parser):
    """就上中文解析"""
    field_num = 11
    ignore_list = []

    def parser_func(self, num, i):
        year = time.strftime('%Y', time.localtime())
        key = None
        value = None
        try:
            key, value = {
                2: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Name', self.contentList[i]], 
                6: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                7: lambda: ['Content', self.contentList[i]], 
                8: lambda: ['Update_Time', year + '-' + 
                             self.contentList[i].replace('月', '-').replace('日', '')
                             + ' 00:00:00'], 
                9: lambda: ['Author', self.contentList[i]], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Qzwap_Parser(Book_Parser):
    """圈子文学解析"""
    field_num = 7
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                2: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Content', self.contentList[i]], 
                4: lambda: ['Author', self.contentList[i]], 
                5: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Ydnovel_Parser(Book_Parser):
    """原点小说解析"""
    field_num = 10
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                4: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Content', self.contentList[i]], 
                2: lambda: ['Author_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Author', self.contentList[i]], 
                8: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Kkkxs_Parser(Book_Parser):
    """三K小说解析"""
    field_num = 8
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                2: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Content', self.contentList[i]], 
                4: lambda: ['Author', self.contentList[i]], 
                6: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Dawenxue_Parser(Book_Parser):
    """大文学解析"""
    field_num = 10
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                4: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Content', self.contentList[i]], 
                6: lambda: ['Author', self.contentList[i]], 
                8: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Baiwandu_Parser(Book_Parser):
    """百万读书解析"""
    field_num = 12
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                5: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                6: lambda: ['Name', self.contentList[i]], 
                7: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                8: lambda: ['Content', self.contentList[i]], 
                10: lambda: ['Author', self.contentList[i]], 
                9: lambda: ['Update_Time', '20' + self.contentList[i] + ':00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Mengxuange_Parser(Book_Parser):
    """梦轩阁解析"""
    field_num = 12
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                4: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Name', self.contentList[i]], 
                6: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                7: lambda: ['Content', self.contentList[i]], 
                9: lambda: ['Author', self.contentList[i]], 
                11: lambda: ['Update_Time', '20' +
                             self.contentList[i].replace('.', '-') + ':00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Novel24_Parser(Book_Parser):
    """新奇点解析"""
    field_num = 11
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                3: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                4: lambda: ['Content', self.contentList[i]], 
                6: lambda: ['Author', self.contentList[i]], 
                9: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Duzheju_Parser(Book_Parser):
    """读者居解析"""
    field_num = 11
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                2: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Name', self.contentList[i]], 
                6: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                7: lambda: ['Content', self.contentList[i]], 
                9: lambda: ['Author', self.contentList[i]], 
                10: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Zhuishu_Parser(Book_Parser):
    """追书网解析"""
    field_num = 11
    ignore_list = []

    def parser_func(self, num, i):
        year = time.strftime('%Y', time.localtime())
        key = None
        value = None
        try:
            key, value = {
                2: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                5: lambda: ['Name', self.contentList[i]], 
                6: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                7: lambda: ['Content', self.contentList[i]], 
                9: lambda: ['Author', self.contentList[i]], 
                10: lambda: ['Update_Time', year + '-' + 
                             self.contentList[i].replace('月', '-').replace('日', '')
                             + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
class Txt6_Parser(Book_Parser):
    """言情书楼解析"""
    field_num = 8
    ignore_list = []

    def parser_func(self, num, i):
        key = None
        value = None
        try:
            key, value = {
                0: lambda: ['Book_Url', self.base_url +
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                1: lambda: ['Name', self.contentList[i]], 
                2: lambda: ['Content_Url', self.base_url + 
                            self.contentList[i] if
                            self.contentList[i].startswith('/') else
                            self.contentList[i]], 
                3: lambda: ['Content', self.contentList[i]], 
                4: lambda: ['Author', self.contentList[i]], 
                6: lambda: ['Update_Time', '20' + self.contentList[i] + ' 00:00:00'], 
            }[num]()
        except KeyError, e:
            pass

        return key, value
        
def main():
	pass


if __name__ == '__main__':
    st = time.time()
    p = Qidian_Parser('qidian')
    #p.fetchUrl('http://book.sina.com.cn/nzt/lit/showsword/index.shtml')
    #p.html_encoding = 'gb2312'
    #p.encoding = 'UTF-8'
    #p.fetchUrl('http://all.qidian.com/Default.aspx')
    f = open('d:\\cmfu.htm')
    html = f.read()
    p.fetchString(html)
    p.parserBook()
    #p.printResult()
    print time.time() - st
