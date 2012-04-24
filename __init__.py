#!/usr/bin/python
# -*- coding: UTF-8 -*- 

_G = {'current_app': None}

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders import app_directories
class Loader(app_directories.Loader):
    is_usable = True
    def load_template_source(self, template_name, template_dirs = None):
        if not _G['current_app']:
            raise TemplateDoesNotExist(template_name)
        app_name = _G['current_app']

        if not template_dirs:
            template_dirs = (d for d in app_directories.app_template_dirs
                if d.endswith('/%s/templates' % app_name))

        return iter(super(Loader, self).load_template_source(
            template_name, template_dirs))

def get_current_app():
    return _G['current_app'] or ''

import inspect
def set_current_app(view_fn):
    def new(*args, **kwargs):
        mod_name = inspect.getmodule(view_fn).__name__
        _G['current_app'] = mod_name.split('.')[0]
        return view_fn(*args, **kwargs)
    return new

from django import template

register = template.Library()

@register.simple_tag
def app_static(path):
    """
    add app prefix to static path.
    """
    return settings.STATIC_URL + get_current_app() + '/' + path

