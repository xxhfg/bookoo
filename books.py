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

from book.models import Book, Author, BookInfo, ContentInfo
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
    #print params

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
            book_parser = None
            j += 1
            #print j
            url = params['url_template'].replace('$$PAGE$$', str(i))
            #print modified, etag
            the_page, modified, etag = pages.get_book_page(url, modified, etag)
            #print modified, etag

            bt = time.time()
            book_parser =func(hostname)
            #print type(the_page)
            book_parser.fetchString(the_page)
            #new_md5 = book_parser.md5()

            #if(new_md5!=None):
                #if(new_md5!=old_md5):
                    #old_md5 = new_md5
                    #"""
            if the_page:
                    for i in range(2, 3):
                        time.sleep(3)
                        url = params['url_template'].replace('$$PAGE$$', str(i))
                        the_page, m, e = pages.get_book_page(url)
                        book_parser.fetchString(the_page)

                    book_parser.parserBook()
                    config.g_mutex.acquire()
                    upd_all_book(book_parser)
                    type(book_parser).last_content_url = book_parser.book_list[0]['Content_Url']
                    print ("共处理 %4d 条记录" %
                           (len(book_parser.book_list))).decode('UTF8')
                    config.g_mutex.release()


        except Exception, e:
            raise e

        print j
        time.sleep(30)

    #config.g_mutex.acquire()
    #print "共处理 %4d 条记录" % (i)
    #config.g_mutex.release()

@transaction.commit_on_success
def upd_all_book(book_parser):
    """更新所有小说信息"""
    #global g_books
    for l in book_parser.book_list:
        l['Alias'] = l['Name'] + '_' + l['Author']
        l['Alias_Host'] = l['Alias'] + '_' + book_parser.host_name
        l['is_new_book'] = config.Yes
        l['is_new_bookinfo'] = config.Yes
        l['is_new_author'] = config.Yes
        for b in config.g_books:
            if (l['Alias'].decode('UTF8')==b['Alias']):
                #print l['Alias'].decode('UTF8'), b['Alias']
                l['book_id'] = b['id']
                l['is_new_book'] = config.No
                break
        if (l['is_new_book']):
            for a in config.g_authors:
                if (l['Author'].decode('UTF8')==a['Name']):
                    #print l['Author'].decode('UTF8'), a['Name']
                    l['author_id'] = a['id']
                    l['is_new_author'] = config.No
                    break
        for bi in config.g_bookinfos:
            if (l['Alias_Host'].decode('UTF8')==bi['Alias']):
                l['bookinfo_id'] = bi['id']
                l['is_new_bookinfo'] = config.No
                break

    k = 0
    for b in book_parser.book_list:
        k = k + 1
        if (b.has_key('is_new_book') and (b['is_new_book'])):
            if (b.has_key('is_new_author') and (b['is_new_author'])):
                author = Author()
                author.Name = b['Author'].decode('UTF8')
                author.save()
                b['author_id'] = author.id
                config.g_authors.append(model_to_dict(author))
            book = Book()
            book.Name = b['Name'].decode('UTF8')
            book.Alias = b['Alias'].decode('UTF8')
            book.author_id = b['author_id']
            book.save()
            b['book_id'] = book.id
            config.g_books.append(model_to_dict(book))
            b['is_new_book'] = config.No
            b['is_new_author'] = config.No
        if (b.has_key('is_new_bookinfo') and (b['is_new_bookinfo'])):
            bookinfo = BookInfo()
            bookinfo.book_id = b['book_id']
            bookinfo.HostName = book_parser.host_name 
            bookinfo.BookUrl = b['Book_Url']
            bookinfo.Alias = b['Alias_Host'].decode('UTF8')
            bookinfo.save()
            config.g_bookinfos.append(model_to_dict(bookinfo))
            b['bookinfo_id'] = bookinfo.id

        if (b['Content_Url']==book_parser.last_content_url):
            break
        else:
            cinfo = ContentInfo()
            cinfo.bookinfo_id = b['bookinfo_id']
            cinfo.LastContent = b['Content'].decode('UTF8')
            cinfo.ContentUrl = b['Content_Url']
            cinfo.LastUpdated = b['Update_Time']
            cinfo.save()

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

def get_all_bookinfo():
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

def get_all_contentinfo():
    info_list = []
    infos = ContentInfo.objects.raw('select max(id), id, bookinfo_id, LastContent,\
                                    ContentUrl, LastUpdated from contentinfo\
                                    GROUP BY bookinfo_id ORDER BY bookinfo_id')
    k = 0
    for i in infos:
        k += 1
        sys.stdout.write(str(k).rjust(10, " "))
        sys.stdout.write('\r')
        sys.stdout.flush()

        info = dict{}
        info[i.bookinfo_id] = i.Content_Url
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
    config.g_bookinfos = get_all_bookinfo()
    print 
    print 'get infos', len(config.g_bookinfos)
    config.g_contentinfos = get_all_contentinfo()
    print 
    print 'get infos', len(config.g_contentinfos)

    webs=['http://all.qidian.com/book/bookstore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=1&update=-1&Vip=-1&Boutique=-1&SignStatus=-1',
          #'http://all.qidian.com/book/bookstore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=100&update=-1&Vip=-1&Boutique=-1&SignStatus=-1', 
         ]
    do_job(['qidian', ])
    #work_manager =  WorkManager(config.WEB_HOSTS, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    #work_manager.wait_allcomplete()  
    #do_job2([config.SZ_LINE_HOME + '/sz000001.lc5', ])
    #main()
    print time.time() - bt
