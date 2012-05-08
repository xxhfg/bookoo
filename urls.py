from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bookoo.views.home', name='home'),
    # url(r'^bookoo/', include('bookoo.foo.urls')),
    url(r'^book/', include('bookoo.book.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    #urlpatterns += patterns('', 
        #url(r"^media/(?P<path>.*)$", "django.views.static.serve", \
                #{"document_root": settings.MEDIA_ROOT,}),
        #url(r"^static/(?P<path>.*)$", "django.views.static.serve", \
                #{"document_root": settings.STATIC_ROOT,}),
        #url(r'^css/(?P<path>.*)$', 'django.views.static.serve',\
                #{'document_root': settings.STATIC_ROOT + '/css', }),
        #url(r'^js/(?P<path>.*)$', 'django.views.static.serve',
                #{'document_root': settings.STATIC_ROOT + '/js', }),
        #url(r'^images/(?P<path>.*)$', 'django.views.static.serve',
                #{'document_root': settings.STATIC_ROOT + '/images', }),
    #)
