from django.conf import settings
from django.conf.urls import patterns, include, url
from huxleyview import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'huxleyview.views.home', name='home'),
    # url(r'^huxleyview/', include('huxleyview.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'huxleyview.views.home', name='home'),
    url(r'^huxley/ajax/get_all_testcase_run_times$', 'huxleyview.views.get_all_testcase_run_times'),
    url(r'^huxley/ajax/get_all_testcase$', 'huxleyview.views.get_all_testcase'),
    url(r'^huxley/ajax/get_latest_testcase$', 'huxleyview.views.get_latest_testcase'),
    url(r'^huxley/(?P<tcasepath>(\w+/).*)/(?P<btime>\d{14})/(?P<etime>\d{14})/$', 'huxleyview.views.history'),

    url(r'^site_media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT},name="site_media"),
)
