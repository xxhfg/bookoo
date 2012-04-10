#!/usr/bin/python
# -*-  coding: UTF8 -*- 

import config
import sys

sys.path.append(config.PROJECT_HOME) #先要把自己的项目目录加入path
from django.core.management import setup_environ #这是重头戏，全靠它了
#from bookoo import settings #介绍自已人
import settings #介绍自已人
setup_environ(settings) #安排自己人
#干活去吧
import time
import socket
import types
from django.db import  transaction
from django.forms.models import model_to_dict

from book.models import Book, Author, BookInfo
from extra.workmanager import *
from extra import webparser, pages
#from config import g_mutex, g_books, g_authors

#global g_mutex
#global g_books
#global g_authors

#具体要做的任务  
# @transaction.commit_on_success
# @transaction.commit_manually
def do_job(args):  
    #global g_mutex
    #global g_books

    if not ((type(args) is types.ListType) and (len(args)==1)):
        return None

    hostname = args[0]
    if(config.WEB_HOSTS.has_key(args[0])):
        params = config.WEB_HOSTS[args[0]]
    else:
        return None
    print params

    if(not hasattr(webparser, params['function'])):
        return None
    func = getattr(webparser, params['function'])

    old_md5 = None
    modified = None
    etag = None
    j = 0
    while True:
        i = 1
        try:
            j += 1
            #print j
            url = params['url_template'].replace('$$PAGE$$', str(i))
            the_page, modified, etag = pages.get_book_page(url, modified, etag)
            print modified, etag, type(the_page)

            bt = time.time()
            #new_md5 = func(the_page, params, old_md5)
            book_parser =func(hostname)
            book_parser.fetchString(the_page)
            new_md5 = book_parser.md5()
            #if(new_md5!=old_md5):
                #book_parser.parserBook()
            #print new_md5, old_md5
            #print time.time() - bt
            #upd_all_book()

            if(new_md5!=None):
                if(new_md5!=old_md5):
                    old_md5 = new_md5
                    #"""
                    for i in range(2, 11):
                        time.sleep(3)
                        url = params['url_template'].replace('$$PAGE$$', str(i))
                        the_page, m, e = pages.get_book_page(url)
                        book_parser.fetchString(the_page)
                        #func(the_page, params, None)
                        #upd_all_book()
                    #"""
                    #upd_all_book(book_parser.book_list)
                    book_parser.parserBook()


            book_parser = None
        except Exception, e:
            #pass
            raise e

        print j
        time.sleep(30)

    config.g_mutex.acquire()
    print "共处理 %4d 条记录" % (i)
    config.g_mutex.release()

@transaction.commit_on_success
def upd_all_book(book_list):
    """更新所有小说信息"""
    #global g_books
    print len(book_list)

    k = 0
    for b in config.g_books:
        k = k + 1
        #print k, b['Name'], b['is_new']
        if (b.has_key('is_new') and (b['is_new'])):
            book = Book()
            book.__dict__.update(b)
            book.save()
            b['id'] = book.id
            b['is_new'] = config.No
            for a in b['authors']:
                author = Author()
                author.__dict__.update(a)
                author.save()
                author.books.add(book)
                author.save()
                #book.author_set.add(author)
        else:
            book = Book(b['id'])

        for i in b['infos']:
            if (i.has_key('upd_new') and (i['upd_new'])):
                info = BookInfo()
                info.__dict__.update(i)
                info.book = book
                #book.bookinfo_set.add(info)
                info.save()
                i['upd_new'] = config.No
    #print config.g_books[len(config.g_books) - 1]

def get_all_book():
    book_list = []
    books = Book.objects.all()
    k = 0
    for b in books:
        k += 1
        sys.stdout.write(str(k).rjust(10, " "))
        sys.stdout.write('\r')
        sys.stdout.flush()

        book = model_to_dict(b)
        #infos = b.bookinfo_set.all()
        #authors = b.author_set.all()
        #book['infos'] = []
        #for i in infos:
            #book['infos'].append(model_to_dict(i))
        #book['authors'] = []
        #for a in authors:
            #book['authors'].append(model_to_dict(a))
        book['is_new'] = config.No
        book_list.append(book)
    return book_list

def get_all_author():
    author_list = []
    authors = Author.objects.all()
    k = 0
    for a in authors:
        k += 1
        sys.stdout.write(str(k).rjust(10, " "))
        sys.stdout.write('\r')
        sys.stdout.flush()

        author = model_to_dict(a)
        author['is_new'] = config.No
        author_list.append(author)

    return author_list

def get_all_info():
    info_list = []
    infos = BookInfo.objects.all()
    k = 0
    for i in infos:
        k += 1
        sys.stdout.write(str(k).rjust(10, " "))
        sys.stdout.write('\r')
        sys.stdout.flush()

        info = model_to_dict(i)
        info['is_new'] = config.No
        info_list.append(info)

    return info_list


def main():
    """处理通达信五分钟数据"""
    #global g_mutex

    # from singleinstance import * 
    config.g_mutex = threading.Lock()
    start = time.time()  

    work_manager =  WorkManager(sh_files, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    end = time.time()  
    print end - start

if __name__ == '__main__':  

    bt = time.time()
    socket.setdefaulttimeout(config.OUT_OF_TIME)
    config.g_mutex = threading.Lock()
    config.g_books = get_all_book()
    print 
    print 'get books', len(config.g_books)
    config.g_authors = get_all_author()
    print 
    print 'get authors', len(config.g_authors)
    config.g_infos = get_all_info()
    print 
    print 'get infos', len(config.g_infos)

    webs=['http://all.qidian.com/book/bookstore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=1&update=-1&Vip=-1&Boutique=-1&SignStatus=-1',
          #'http://all.qidian.com/book/bookstore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=100&update=-1&Vip=-1&Boutique=-1&SignStatus=-1', 
         ]
    do_job(['qidian', ])
    #work_manager =  WorkManager(config.WEB_HOSTS, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    #work_manager.wait_allcomplete()  
    #do_job2([config.SZ_LINE_HOME + '/sz000001.lc5', ])
    #main()
    print time.time() - bt
