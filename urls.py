from django.conf.urls.defaults import *
from django.contrib import admin
from tcd.feeds import NewTopics, NewArguments, BlogFeed, UserFeed

admin.autodiscover()

feeds = {
    'newtopics': NewTopics,
    'newargs':   NewArguments,
    'blog': BlogFeed,
    'user': UserFeed
}

urlpatterns = patterns('',
                       # Admin app
                       (r'^admin/(.*)', admin.site.root),
                       
                       # About Us page - static
                       (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),

                       # Urls associated with the commenting system
                       (r'^comments/', include('tcd.comments.urls')),                                              
                       
                       # Frequently Asked Questions
                       (r'^FAQ/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}),

                       # Help page - static
                       (r'^help/$', 'django.views.generic.simple.direct_to_template', {'template': 'help.html'}),                       

                       # Terms of Service - Static
                       (r'^tos/$', 'django.views.generic.simple.direct_to_template', {'template': 'tos.html'}),

                       # Privacy Policy - Static
                       (r'^privacy/$', 'django.views.generic.simple.direct_to_template', {'template': 'privacy.html'}),
                       
                       # Buttons for bloggers
                       (r'^buttons/$', 'django.views.generic.simple.direct_to_template', {'template': 'buttons.html'}),

                       # RSS feeds
                       (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
                        {'feed_dict': feeds}),
                       
                       # Blog system
                       (r'^blog/(?P<username>[A-Za-z\d]+)/', include('tcd.blog.urls')),

                       # Urls associated with user profiles
                       (r'^users/', include('tcd.profiles.urls')),

                       (r'', include('tcd.items.urls'))
)
