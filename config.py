#!/usr/bin/python
# -*- coding: UTF-8 -*- 

__author__ = 'Administrator'

import os
import sys

#项目路径
PROJECT_HOME = os.path.dirname(__file__) + '/'
#默认超时
OUT_OF_TIME = 10
#默认输出代码
SYS_OUT_ENCODING = sys.stdin.encoding
#默认代码
SYS_ENCODING = 'UTF-8'
#Yes代表1
Yes = 1
#No代表0
No = 0

#网站配置信息
WEB_HOSTS = {
    'qidian':{
        'name':'起点中文网', 
        'host':'http://www.qidian.com', 
        'code':'UTF-8', 
        'alias':'qidian', 
        'function':'Qidian_Parser', 
        'url_template':'http://all.qidian.com/book/bookstore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=$$PAGE$$&update=-1&Vip=-1&Boutique=-1&SignStatus=-1',
        #替换掉$$PAGE$$, 生成查询地址
        #'url_template':'/Users/xxhfg/cmfu.html', 
        'page_start':'<!--[if !IE]> 结果列表 开始 <![endif]-->', 
        'page_stop':'<!--[if !IE]> 结果列表 结束 <![endif]-->', 
        'book_pattern':'<span class="swbt"><a href="(?P<book_url>.*?)".*?>(?P<book_name>.*?)</.*?href="(?P<content_url>.*?)".*?>(?P<content_name>.*?)</.*?href="(?P<author_url>.*?)".*?>(?P<author_name>.*?)</.*?">(?P<update_time>.*?)</', 
    }, 
    'test':{
        'name':'test', 
    }
}
