__author__ = 'Administrator'

from django.conf.urls.defaults import *
from django.conf import settings
from bookoo.book.views import *

urlpatterns = patterns('',
    url(r'^$', index),
)
