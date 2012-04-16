#!/usr/bin/python
# -*- coding: UTF-8 -*- 

from django.db import models

# Create your models here.
class Author(models.Model):
    """作者信息"""
        
    Name = models.CharField(max_length=30)
    Alias = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'authors'

class Book(models.Model):
    """小说基本信息"""
        
    Name = models.CharField(max_length=30)
    Alias = models.CharField(max_length=100)
    author = models.ForeignKey(Author)

    class Meta:
        db_table = 'books'

class BookInfo(models.Model):
    """小说网络信息"""

    book = models.ForeignKey(Book)
    HostName = models.CharField(max_length=30)
    BookUrl = models.URLField()
    Alias = models.CharField(max_length=100)
    #LastContent = models.CharField(max_length=50)
    #ContentUrl = models.URLField()
    #LastUpdated = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        db_table = 'bookinfo'

class ContentInfo(models.Model):
    """小说更新信息"""
    bookinfo = models.ForeignKey(BookInfo)
    LastContent = models.CharField(max_length=50)
    ContentUrl = models.URLField()
    LastUpdated = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        db_table = 'contentinfo'
