from django.conf.urls.defaults import *
from tcd.items.models import Topic

# This file is included in tcd.urls with no prefix

urlpatterns = patterns('',
                       # View Topics sorted by highest score
                       (r'^$', 'tcd.items.views.topics'), 
                       (r'^page/(?P<page>\d+)/$', 'tcd.items.views.topics'),                          

                       # View Topics sorted by submission date
                       (r'^(?P<sort>(new))/$', 'tcd.items.views.topics'),
                       (r'^(?P<sort>(new))/(?P<page>\d+)/$', 'tcd.items.views.topics'),
                       
                       # View Comments associated with a topic
                       (r'^(?P<topic_id>\d+)/$', 'tcd.items.views.comments'),
                       (r'^(?P<topic_id>\d+)/(?P<page>\d+)$', 'tcd.items.views.comments'),
                       
                       # Submit a new topic
                       (r'^submit/$', 'tcd.items.views.submit'),
                       
                       # Vote for a participant in an argument
                       (r'^vote/$', 'tcd.items.views.vote'),

                       # Edit the title, url or description of a topic
                       (r'^edit/(?P<topic_id>\d+)/(?P<page>\d+)$', 'tcd.items.views.edit_topic'),

                       # Flag a topic as spam
                       (r'^tflag/$', 'tcd.items.views.tflag'),

                       # Urls associated with the commenting system
                       (r'^comments/', include('tcd.comments.urls')),                                              

                       # Urls associated with arguments
                       (r'^argue/', include('tcd.items.argue_urls')),
                       
                       # Urls associated with user profiles
                       (r'^users/', include('tcd.profiles.urls')),
                       
)
