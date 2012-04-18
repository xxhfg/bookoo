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
#from extra.workmanager import *
from extra.work import * 
from extra import webparser, pages
#from config import g_mutex, g_books, g_authors

#global g_mutex
#global g_books
#global g_authors

#具体要做的任务  
def do_job(arg):
    hostname = arg
    print hostname + ' processing......'
    if(config.WEB_HOSTS.has_key(hostname)):
        params = config.WEB_HOSTS[hostname]
    else:
        return -1

    if((not params.has_key('is_valid')) or (not params['is_valid'])):
        return -1

    if(not hasattr(webparser, params['function'])):
        return -1
    func = getattr(webparser, params['function'])

    modified = None
    etag = None
    try:
        i = 1
        url = params['url_template'].replace('$$PAGE$$', str(i))
        the_page, modified, etag = pages.get_book_page(url, modified, etag)
        if (the_page):
            book_parser = None
            book_parser =func(hostname)
            book_parser.fetchString(the_page)

            for i in range(2, 4):
                time.sleep(3)
                url = params['url_template'].replace('$$PAGE$$', str(i))
                the_page, m, e = pages.get_book_page(url)
                book_parser.fetchString(the_page)

            book_parser.parserBook()
            if config.g_mutex.acquire():
                #print hostname + '    lock......'
                bt = time.time()
                upd_all_book(book_parser)
                print "step 3 use time: %f" % (time.time()-bt)
                config.g_mutex.release()
                type(book_parser).last_content_url = book_parser.book_list[0]['Content_Url']
                print ("%s 共处理 %4d 条记录" %
                       (book_parser.host_name, 
                        len(book_parser.book_list))).decode(config.SYS_ENCODING)
                #print hostname + '    unlock......'
            return 0
        else:
            return -2
    except Exception, e:
        print hostname, sys.exc_info()
        return -3

@transaction.commit_on_success
def upd_all_book(book_parser):
    """更新所有小说信息"""
    #global g_books
    bt = time.time()
    for l in book_parser.book_list:
        l['Alias'] = l['Name'] + '_' + l['Author']
        l['Alias_Host'] = l['Alias'] + '_' + book_parser.host_name
        l['Alias_Author'] = l['Author'] + '_' + book_parser.host_name
        l['is_new_book'] = config.Yes
        l['is_new_bookinfo'] = config.Yes
        l['is_new_contentinfo'] = config.Yes
        l['is_new_author'] = config.Yes
        for b in config.g_books:
            if (l['Alias'].decode(config.SYS_ENCODING)==b['Alias']):
                l['book_id'] = b['id']
                l['is_new_book'] = config.No
                break

        if (l['is_new_book']):
            for a in config.g_authors:
                if (l['Alias_Author'].decode(config.SYS_ENCODING)==a['Alias']):
                    #print l['Author'].decode(config.SYS_ENCODING), a['Name']
                    l['author_id'] = a['id']
                    l['is_new_author'] = config.No
                    break
        for bi in config.g_bookinfos:
            if (l['Alias_Host'].decode(config.SYS_ENCODING)==bi['Alias']):
                l['bookinfo_id'] = bi['id']
                l['is_new_bookinfo'] = config.No
                break
        #if (l.has_key('bookinfo_id')) and (config.g_contentinfos.has_key(l['bookinfo_id'])):
        try:
            if (config.g_contentinfos[l['bookinfo_id']] == l['Content_Url']):
                l['is_new_contentinfo'] = config.No
            #else:
                #config.g_contentinfos[l['bookinfo_id']] = l['Content_Url']
        except KeyError:
            pass

    print "step 1 use time: %f" % (time.time()-bt)
    bt = time.time()
    k = 0
    for b in book_parser.book_list:
        if (book_parser.is_origin):
          if (b.has_key('is_new_book') and (b['is_new_book'])):
            if (b.has_key('is_new_author') and (b['is_new_author'])):
                author = Author()
                author.Name = b['Author'].decode(config.SYS_ENCODING)
                author.Alias = b['Alias_Author'].decode(config.SYS_ENCODING)
                author.save()
                b['author_id'] = author.id
                config.g_authors.append(model_to_dict(author))
            book = Book()
            book.Name = b['Name'].decode(config.SYS_ENCODING)
            book.Alias = b['Alias'].decode(config.SYS_ENCODING)
            book.author_id = b['author_id']
            book.save()
            config.g_books.append(model_to_dict(book))
            b['book_id'] = book.id
            b['is_new_book'] = config.No
            b['is_new_author'] = config.No
        if (b.has_key('is_new_bookinfo') and b.has_key('is_new_book')):
          if ((b['is_new_bookinfo']) and (not b['is_new_book'])):
            bookinfo = BookInfo()
            bookinfo.book_id = b['book_id']
            bookinfo.HostName = book_parser.host_name 
            bookinfo.BookUrl = b['Book_Url']
            bookinfo.Alias = b['Alias_Host'].decode(config.SYS_ENCODING)
            bookinfo.LastContent = b['Content'].decode(config.SYS_ENCODING)
            bookinfo.ContentUrl = b['Content_Url']
            bookinfo.LastUpdated = time.time()
            bookinfo.save()
            config.g_bookinfos.append(model_to_dict(bookinfo))
            b['bookinfo_id'] = bookinfo.id
            b['is_new_bookinfo'] = config.No
          """
          else:
            bookinfo = BookInfo.objects.get(id=b['bookinfo_id'])
            bookinfo.LastContent = b['Content'].decode(config.SYS_ENCODING)
            bookinfo.ContentUrl = b['Content_Url']
            bookinfo.LastUpdated = time.strftime('%Y-%m-%d %H:%M',
                                                 time.localtime())
            bookinfo.save()
          """
        if (b.has_key('is_new_contentinfo') and b.has_key('is_new_book')):
          if ((b['is_new_contentinfo']) and (not b['is_new_book'])):
            k = k + 1
            cinfo = ContentInfo()
            cinfo.bookinfo_id = b['bookinfo_id']
            cinfo.LastContent = b['Content'].decode(config.SYS_ENCODING)
            cinfo.ContentUrl = b['Content_Url']
            cinfo.LastUpdated = time.strftime('%Y-%m-%d %H:%M',
                                                 time.localtime())
            cinfo.save()
            config.g_contentinfos[b['bookinfo_id']] = b['Content_Url']
            b['is_new_contentinfo'] = config.No
    print "step 2 use time: %f" % (time.time()-bt)
    print "valid record %4d" % (k)

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
    info_list = {}
    infos = ContentInfo.objects.raw('select max(id), id, bookinfo_id, LastContent,\
                                    ContentUrl, LastUpdated from contentinfo\
                                    GROUP BY bookinfo_id ORDER BY bookinfo_id')
    k = 0
    for i in infos:
        k += 1
        sys.stdout.write(str(k).rjust(10, " "))
        sys.stdout.write('\r')
        sys.stdout.flush()

        #info = dict{}
        #info[i.bookinfo_id] = i.Content_Url
        #info_list.append(info)
        info_list[i.bookinfo_id] = i.ContentUrl

    return info_list

def main():
    import socket
    socket.setdefaulttimeout(10)

    config.g_books = get_all_book()
    print 
    print 'get books', len(config.g_books)
    config.g_authors = get_all_author()
    print 
    print 'get authors', len(config.g_authors)
    config.g_bookinfos = get_all_bookinfo()
    print 
    print 'get bookinfos', len(config.g_bookinfos)
    config.g_contentinfos = get_all_contentinfo()
    print 
    print 'get contentinfos', len(config.g_contentinfos)

    while True:
        #do_job('38836')
        wm = WorkerManager(4)
        for k in config.WEB_HOSTS:
            wm.add_job( do_job, k)
        wm.wait_for_complete()

        #work_manager =  WorkManager(config.WEB_HOSTS, do_job, 5)#或者work_manager =  WorkManager(10000, 20)  
        #work_manager.wait_allcomplete()  

        print 'sleeping......'
        time.sleep(300)

if __name__ == '__main__':  

    config.g_mutex = threading.Lock()
    bt = time.time()
    main()
    print time.time() - bt
