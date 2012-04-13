#!/usr/bin/env python
# encoding: utf-8
"""
pages.py

Created by  on 2011-12-21.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import re
import hashlib
import urllib2
import openanything
from config import  SYS_ENCODING, Yes, No
import config

def get_book_page(Url, modified=None, etag=None):
    """
    从网络上获取网页内容
    """
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    values = {}
    headers = { 'User-Agent' : user_agent }
    data = urllib2.quote(values)
    #modified = None
    #etag = None
    try:
        ns = openanything.fetch(Url, None, modified, user_agent)

        if (ns.has_key('lastmodified')):
            modified = ns['lastmodified']
        else:
            modified = None
        if (ns.has_key('etag')):
            etag = ns['etag']
        else:
            etag = None

        if (ns.has_key('code')):
            if (ns['code']==200):
                #print ns['header']
                return ns['data'], modified, etag
        else:
            return ns['data'], None, None
    except Exception, e:
        #raise e
        pass

    return None, modified, etag

def qidian_book(the_page, params, old_md5=None):
    """
    分解起点书库的更新记录
    """
    #global g_books

    if ((the_page==None) or (the_page=='')):
        return None

    #html_utf8 = the_page.decode(params['code']).encode('UTF-8')
    #start_pos = html_utf8.find(params['page_start'])
    #stop_pos = html_utf8.find(params['page_stop'])

    start_pos = the_page.find(params['page_start'].decode(SYS_ENCODING).encode(params['code']))
    stop_pos = the_page.find(params['page_stop'].decode(SYS_ENCODING).encode(params['code']))
    if((start_pos==-1) or (stop_pos==-1)):
        return None

    content = the_page[start_pos:stop_pos]
    new_md5 = hashlib.md5(content).digest()
    print old_md5, new_md5
    if(new_md5==old_md5):
        return old_md5

    try:
        pattern = re.compile(params['book_pattern'], re.I)
        book_list = pattern.finditer(content)
        proc_book_list(book_list)

    except Exception, e:
        raise e

    return new_md5

def proc_book_list(book_list):
    if (0==len(book_list)):
        return False

    for book_info in book_list:
        try:
            book_name = book_info.group('book_name').decode(params['code']).encode(SYS_ENCODING)
            author_name = book_info.group('author_name').decode(params['code']).encode(SYS_ENCODING)
            print book_name, author_name
            book_alias = book_name + '_' + author_name
            book_url = book_info.group('book_url').decode(params['code']).encode(SYS_ENCODING)
            content_url = book_info.group('content_url').decode(params['code']).encode(SYS_ENCODING)
            content_name = book_info.group('content_name').decode(params['code']).encode(SYS_ENCODING)
            update_time = book_info.group('update_time').decode(params['code']).encode(SYS_ENCODING)
            is_new = Yes
            upd_new = Yes
            for b in config.g_books:
                if (unicode(book_alias, SYS_ENCODING)==b['Alias']):
                    print 'in'
                    is_new = No
                    for i in b['infos']:
                        if (unicode(params['name'], SYS_ENCODING)==i['HostName']):
                            print 'inin'
                            upd_new = No
                            break
                    break
            if (is_new==Yes):
                book = {}
                book['Name'] = unicode(book_name, SYS_ENCODING)
                book['Alias'] = unicode(book_alias, SYS_ENCODING)
                book['authors'] = []
                book['infos'] = []

                author = {}
                author['Name'] = unicode(author_name, SYS_ENCODING)
                book['authors'].append(author)

                book['is_new'] = is_new
                info = {}
                info['HostName'] = unicode(params['name'], SYS_ENCODING)
                if (book_url.startswith('http')):
                    info['BookUrl'] = book_url
                else:
                    info['BookUrl'] = params['host'] + book_url
                info['LastContent'] = unicode(content_name, SYS_ENCODING)
                if (content_url.startswith('http')):
                    info['ContentUrl'] = content_url
                else:
                    info['ContentUrl'] = params['host'] + content_url
                if (update_time.startswith('20')):
                    info['LastUpdated'] = update_time
                else:
                    info['LastUpdated'] = '20' + update_time
                info['upd_new'] = upd_new
                book['infos'].append(info)

                config.g_books.append(book)

            elif (upd_new==Yes):
                info = {}
                info['HostName'] = params['name']
                if (book_url.startswith('http')):
                    info['BookUrl'] = book_url
                else:
                    info['BookUrl'] = params['host'] + book_url
                info['LastContent'] = content_name
                if (content_url.startswith('http')):
                    info['ContentUrl'] = content_url
                else:
                    info['ContentUrl'] = params['host'] + content_url
                if (update_time.startswith('20')):
                    info['LastUpdated'] = update_time
                else:
                    info['LastUpdated'] = '20' + update_time
                info['upd_new'] = upd_new
                b['infos'].append(info)

            #time.sleep(3)
            print len(config.g_books)

        except UnicodeDecodeError, e:
            pass
        except Exception, e:
            raise e
 
def main():
	pass


if __name__ == '__main__':
	main()

