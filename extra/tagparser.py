#!/usr/bin/env python
#coding=utf-8
import cStringIO as StringIO 
import urllib2
import time

def getAbsUrl(url = '',p = ''):
    absurl = p
    if not p or p.startswith("http://"):
        return absurl
    if p.find('/') != -1:
        host = ''
        i = 0
        index = 0
        for c in url:
            index += 1
            if c == '/':
                i += 1
            if i == 3:
                host = url[:index-1]
                absurl = host + p
                #print 'host ::: ',url ,host ," p " ,p
                break
    else:
        absurl = url[:url.rfind('/')+1] + p
    return absurl

TAG_ST_NAME = 1
TAG_ST_KEY = 2
TAG_ST_VALUE = 3

def getHeader(url ,ref = ''):
    if not url.startswith('http://'):
        url = 'http:/' + url
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
    request.add_header('Referer', ref)
    return request

def getTag(tag = ''):
    ret = {}
    state = TAG_ST_NAME
    if tag:
        buffer = StringIO.StringIO()
        key = ''
        endchar = tag[-1]
        maxlen = len(tag) -1 
        for i,c in enumerate(tag):
            if state == TAG_ST_NAME and c == ' ':
                v = buffer.getvalue()
                buffer.truncate(0)
                if v:
                    ret['tag_name'] = v.lower()
                    state = TAG_ST_KEY
                continue
            elif state == TAG_ST_KEY and c == '=':
                key = buffer.getvalue().strip().lower()
                buffer.truncate(0)
                state = TAG_ST_VALUE
                continue
            elif state == TAG_ST_VALUE:
                if c in ('\'','"',';') or i == maxlen:
                    v = buffer.getvalue().strip()
                    if v and key:
                        buffer.truncate(0)
                        ret[key] = v
                        key = ''
                        state = TAG_ST_KEY
                    continue
            buffer.write(c)
    return ret

#t = getTag(r'link rel="next" href="extracting_data.html" title="8.3.&nbsp;从 HTML 文档中提取数据"')
#for k,value in t.items():
#    print k , value.decode('utf8').encode('gbk')


            

class TagParser(object):
       
    def __init__(self):
        self.htmlData = '' # 将要获得的html
        self.end = False   # 这个值设置为true时 就会结束此次处理
        self.html_encoding = '' # 获得的结果的编码,也就是网页的字符编码
        self.encoding = '' # 输出的字符编码
        self.title = ''    # 网页的title
        self.lastTag = ''  # 上一个tag 
        self.url = ''      # 实际网页的url ,刚指定的url可能被重定向到其他的url
        self.contentList = [] # 获得内容的列表 全是文字
        self.tagList = []     # 获得html所有的tag
        self.mainBegin = False 
        self.beginTag = '' # 设置处理到哪一个tag就停止处理
        self.endTag = ''   # 设置处理到哪一个tag就停止处理
        self.tagA = None   # 是一个<a>
        self.referurl = '' #
        
    def fetchUrl(self, url = ''):
        if url:
            try:
                bt = time.time()
                if self.referurl:
                    req = getHeader(url,self.referurl)
                else:
                    req = getHeader(url)
                web = urllib2.urlopen(req)
                html = web.read()
                url = web.geturl()
                print 'get html use time: ' , time.time() - bt
            except Exception ,ex:
                print 'sth wrong to get url:' ,ex
                html = ''
            if html:
                self.url = url
                if (self.html_encoding and self.encoding):
                    self.htmlData = html.decode(self.html_encoding, 'ignore').encode(self.encoding, 'ignore')
                else:
                    self.htmlData = html
                if not self.beginTag:
                    self.mainBegin = True
                bt = time.time()
                self.doParser()
                print 'parser use time: ' ,time.time() - bt

    def fetchString(self, html=''):
        if html:
            #self.url = url
            if (self.html_encoding and self.encoding):
                self.htmlData = html.decode(self.html_encoding, 'ignore').encode(self.encoding, 'ignore')
            else:
                self.htmlData = html
            if not self.beginTag:
                self.mainBegin = True
            bt = time.time()
            self.doParser()
            print 'parser use time: ' ,time.time() - bt 

    def printResult(self, content=True):
        if content:
            ret = '\n'.join(self.contentList)
            #if self.encoding == 'gb2312':
                #print ret
            #ret = ret.decode(self.encoding, 'ignore').encode('gb2312', 'ignore')
            #ret = ret.decode(self.html_encoding, 'ignore').encode(self.encoding, 'ignore')
        else:
            ret = '\n'.join(self.tagList)
        print ret
        
    def onGetTxt(self, txtstr):
        self.contentList.append( txtstr )
        #print 'warnning ! please implements onGetTxt function !!!!'

    def onGetTag(self, tagstr, tagstro):
        self.tagList.append(tagstro)
        #print 'warnning ! please implements onGetTxt onGetTag !!!!'

    def getLastTagAhref(self):
        link = ''
        if self.tagA:
            td = getTag(self.tagA)
            link = getAbsUrl(self.url,td.get('href',''))
            self.tagA = None
        if link:
            link = link[7:]
        return link

    def getImgTagSrc(self, tag):
        link = ''
        if tag:
            td = getTag(tag)
            link = getAbsUrl(self.url,td.get('src',''))
        if link:
            link = link[7:]
        return link
    
    def doParser(self):
        stopRecord = ''
        strBuffer = StringIO.StringIO()
        for c in self.htmlData:
            if self.end:
                break
            if c == '<':
                if stopRecord:
                    strBuffer.truncate(0)
                    #if cont: print 'dont record ' , stopRecord ,'no use ',cont[:10]
                    continue
                cont = strBuffer.getvalue()
                strBuffer.truncate(0)
                cont = cont.replace('&nbsp;',' ').strip();
                if cont:
                    if not self.title and self.lastTag.startswith('title'):
                        self.title = cont.replace('\"','\\"')
                        continue
                    if self.mainBegin:
                        self.onGetTxt(cont)                    
            elif c == '>':
                    tagstro = strBuffer.getvalue().strip()
                    if not self.mainBegin and self.beginTag :
                        if tagstro == self.beginTag:
                            self.mainBegin = True
                    if self.endTag and tagstro == self.endTag:
                        return
                    #if tagstro.startswith('![CDATA['):
                    #    self.onGetTxt(tagstro[8:-2])
                    if tagstro.startswith('a '):
                        sidx = tagstro.find('href=')
                        if(sidx >= 0):
                            s = tagstro[sidx + 5]
                            eidx = tagstro.find(s, sidx + 6)
                            tagstro = tagstro[sidx + 6:eidx]
                        self.onGetTxt(tagstro)
                    tagstr = tagstro.lower()
                    strBuffer.truncate(0)
                    if stopRecord:
                        if tagstr == stopRecord:
                            stopRecord = '' 
                        elif tagstr.endswith(stopRecord):
                            stopRecord = '' 
                    if stopRecord:# 在javascript代码?或者嵌套在stop区域内的tag不解析不处理,直接continue
                        continue
                    if tagstr:
                        if self.lastTag.startswith('a '):
                            if tagstr == '/a':
                                self.lastTag = tagstr
                        else:
                            self.lastTag = tagstr
                        if not self.encoding :
                            if tagstr.startswith('meta ') and tagstr.find('charset')!= -1:
                                if tagstr.find('utf') != -1:
                                     self.encoding = 'utf8'
                                elif tagstr.find('gb2312')!=-1:
                                     self.encoding = 'gb2312'
                                else:
                                    self.encoding = 'gbk'
                        elif tagstr.startswith('script'):
                            stopRecord = '/script'  # 发现是script 的时候暂停记录strBuffer?ret
                            #print 'stop script' , tagstr
                        elif tagstr.startswith('style'):
                            stopRecord = '/style' 
                        #elif tagstr.startswith('select'):
                        #    stopRecord = '/select'
                        elif tagstr.startswith('!--'):
                            if len(tagstr) == 3 or not tagstr.endswith('--') :
                                stopRecord = '--'
                            self.onGetTag(tagstr,tagstro)
                        else:
                            if tagstr.startswith('a '):
                                self.tagA = tagstro
                            self.onGetTag(tagstr,tagstro)

            else:
                if  c != '\n':
                    strBuffer.write(c) 


TAG_H1 = 1
TAG_A = 2
TAG_IMG = 3
TAG_P = 4
TAG_TITLE = 5
TAG_TD = 6

if __name__ == '__main__':
    p = TagParser()
    #p.fetchUrl('http://book.sina.com.cn/nzt/lit/showsword/index.shtml')
    p.html_encoding = 'gb2312'
    p.encoding = 'UTF-8'
    p.fetchUrl('http://all.qidian.com/Default.aspx')
    p.printResult()
    """
    import urllib2
    web = urllib2.urlopen('http://book.sina.com.cn/nzt/lit/showsword/index.shtml')
    print web.info() 
    html = web.read()
    print html
    """
    
