#!/usr/bin/python
# -*- coding: UTF-8 -*- 

# Create your views here.
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from models import ContentInfo 

def index(request):
    """

    """
    t = get_template('index.html')
    objs = ContentInfo.objects.all()
    html = t.render(Context({'title':'书库', 'objects':objs}))
    return HttpResponse(html)

