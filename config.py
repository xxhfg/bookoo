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
#默认时间格式
ISOTIMEFORMAT='%Y-%m-%d %X'
#Yes代表1
Yes = 1
#No代表0
No = 0
#全局锁
g_mutex = None
g_books = []
g_bookinfos = []
g_authors = []
g_contentinfos = []

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
        'is_origin':True, 
    }, 
    'skxsw':{
        'name':'搜客小说网', 
        'host':'http://www.skxsw.com', 
        'code':'GBK', 
        'alias':'skxsw', 
        'function':'Skxsw_Parser', 
        'url_template':'http://www.skxsw.com/files/article/toplastupdate/0/$$PAGE$$.htm', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'class="head">状态</td>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'dukankan':{
        'name':'读看看', 
        'host':'http://www.dukankan.com', 
        'code':'GB2312', 
        'alias':'dukankan', 
        'function':'Dukankan_Parser', 
        'url_template':'http://www.dukankan.com/book/showbooklist.aspx?page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'class="head">状态</td>', 
        'page_stop':'<div id="CrListPage">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'wjskw':{
        'name':'万卷书库', 
        'host':'http://www.wjskw.com', 
        'code':'GBK', 
        'alias':'wjskw', 
        'function':'Wjskw_Parser', 
        'url_template':'http://www.wjskw.com/novellist.php?sortid=&page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'<span class="Time"> 更新时间</span>', 
        'page_stop':'<div align=right id="page">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    '53sj':{
        'name':'53书居', 
        'host':'http://www.53sj.com', 
        'code':'GBK', 
        'alias':'53sj', 
        'function':'Sj53_Parser', 
        'url_template':'http://www.53sj.com/toplist/lastupdate-$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>状态</th>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    '93zw':{
        'name':'就上书居', 
        'host':'http://www.93zw.com', 
        'code':'GB2312', 
        'alias':'93zw', 
        'function':'Zw93_Parser', 
        'url_template':'http://www.93zw.com/Book/ShowBooklist.aspx?page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'<div id=showlistnr>', 
        'page_stop':'<div id="showlistpage">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'qzwap':{
        'name':'圈子文学', 
        'host':'http://www.qzwap.com', 
        'code':'GBK', 
        'alias':'qzwap', 
        'function':'Qzwap_Parser', 
        'url_template':'http://www.qzwap.com/book/toplastupdate/0/$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'class="head">状态</td>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'ydnovel':{
        'name':'原点小说', 
        'host':'http://ydnovel.com/', 
        'code':'GBK', 
        'alias':'ydnovel', 
        'function':'Ydnovel_Parser', 
        'url_template':'http://ydnovel.com/book/toplastupdate/0/$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>状态</div></li>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'kkkxs':{
        'name':'三K小说', 
        'host':'http://www.kkkxs.com/', 
        'code':'GBK', 
        'alias':'kkkxs', 
        'function':'Kkkxs_Parser', 
        'url_template':'http://www.kkkxs.com/files/article/toplastupdate/0/$$PAGE$$.htm', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'class="head">状态</td>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'dawenxue':{
        'name':'大文学', 
        'host':'http://www.dawenxue.net/', 
        'code':'GBK', 
        'alias':'dawenxue', 
        'function':'Dawenxue_Parser', 
        'url_template':'http://www.dawenxue.net/xiaoshuotoplastupdate/0/$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>状态</th>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'baiwandu':{
        'name':'百万读书', 
        'host':'http://www.baiwandu.com/', 
        'code':'GB2312', 
        'alias':'baiwandu', 
        'function':'Baiwandu_Parser', 
        'url_template':'http://www.baiwandu.com/Book/ShowBookList.aspx?page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'<!--list begin-->', 
        'page_stop':'<!-- AspNetPager', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    '38836':{
        'name':'梦轩阁', 
        'host':'http://www.38836.com/', 
        'code':'GB2312', 
        'alias':'Mengxuange', 
        'function':'Mengxuange_Parser', 
        'url_template':'http://www.38836.com/BookList.aspx?page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'<div id="CrListText">', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    '24novel':{
        'name':'新奇点', 
        'host':'http://www.24novel.com/', 
        'code':'GBK', 
        'alias':'24novel', 
        'function':'Novel24_Parser', 
        'url_template':'http://www.24novel.com/files/article/toplastupdate/0/$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>状态</div>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'duzheju':{
        'name':'读者居', 
        'host':'http://www.duzheju.com/', 
        'code':'GBK', 
        'alias':'duzheju', 
        'function':'Duzheju_Parser', 
        'url_template':'http://www.duzheju.com/sort.php?sortid=0&orderbyid=&page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'<div id="update_Content0">', 
        'page_stop':'<div class="bookpage">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'zhuishu':{
        'name':'追书网', 
        'host':'http://zhuishu.com/', 
        'code':'GB2312', 
        'alias':'zhuishu', 
        'function':'Zhuishu_Parser', 
        'url_template':'http://zhuishu.com/Book/ShowBookList.aspx?page=$$PAGE$$', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>更新时间</li>', 
        'page_stop':'<div class="bookpage">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
    'txt6':{
        'name':'言情书楼', 
        'host':'http://www.txt6.net/', 
        'code':'GBK', 
        'alias':'txt6', 
        'function':'Txt6_Parser', 
        'url_template':'http://www.txt6.net/ztoplastupdate/0/$$PAGE$$.html', 
        #替换掉$$PAGE$$, 生成查询地址
        'page_start':'>状态</th>', 
        'page_stop':'<div class="pages">', 
        'book_pattern':'', 
        'is_origin':False, 
    }, 
}
