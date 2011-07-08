from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.base import TemplateView
from tcd.feeds import NewTopics, NewArguments, BlogFeed, UserFeed, UserFeedAtom

admin.autodiscover()

rssfeeds = {
    'newtopics': NewTopics,
    'newargs':   NewArguments,
    'blog': BlogFeed,
    'user': UserFeed,
    }

atomfeeds = {
    'user': UserFeedAtom
    }

urlpatterns = patterns('',
                       # Admin app
                       (r'^admin/', include(admin.site.urls)),
                       
                       # About Us page - static
                       (r'^about/$', TemplateView(template_name='about.html')),

                       # Urls associated with the commenting system
                       (r'^comments/', include('tcd.comments.urls')),                                              
                       
                       # Frequently Asked Questions
                       (r'^FAQ/$', TemplateView(template_name='faq.html')),

                       # Help page - static
                       (r'^help/$', TemplateView(template_name='help.html')),                       

                       # Terms of Service - Static
                       (r'^tos/$', TemplateView(template_name='tos.html')),

                       # Privacy Policy - Static
                       (r'^privacy/$', TemplateView(template_name='privacy.html')),
                       
                       # Buttons for bloggers
                       (r'^buttons/$', TemplateView(template_name='buttons.html')),

                       # Topics feeds
                       (r'^feeds/newtopics/$', NewTopics()),

                       # Debate feeds
                       (r'^feeds/newargs/$', NewArguments()),                       
                       
                       # Blog feed
                       (r'^feeds/blog/(?P<blog_id>\d+)/$', BlogFeed()),                       
                       
                       # UserFeed
                       (r'^feeds/user/(?P<username>[A-Za-z\d]+)/$', UserFeed()),

                       # Blog system
                       (r'^blog/(?P<username>[A-Za-z\d]+)/', include('tcd.blog.urls')),

                       # Urls associated with user profiles
                       (r'^users/', include('tcd.profiles.urls')),

                       (r'', include('tcd.items.urls'))
                       )
