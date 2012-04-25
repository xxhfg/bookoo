#!/usr/bin/python
# -*- coding: UTF-8 -*- 

# Create your views here.
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def index(request):
    t = get_template('index.html')
    html = t.render(Context({'title':'书库'}))
    return HttpResponse(html)

