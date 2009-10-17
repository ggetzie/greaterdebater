from django.conf.urls.defaults import *
from django.contrib import admin
from tcd.feeds import NewTopics, NewArguments

admin.autodiscover()

feeds = {
    'newtopics': NewTopics,
    'newargs':   NewArguments
}

urlpatterns = patterns('',
                       (r'^admin/(.*)', admin.site.root),
                       (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
                       (r'^FAQ/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}),
                       (r'^help/$', 'django.views.generic.simple.direct_to_template', {'template': 'help.html'}),                       
                       (r'^tos/$', 'django.views.generic.simple.direct_to_template', {'template': 'tos.html'}),
                       (r'^privacy/$', 'django.views.generic.simple.direct_to_template', {'template': 'privacy.html'}),
                       (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
                        {'feed_dict': feeds}),
                       (r'', include('tcd.items.urls'))
)
