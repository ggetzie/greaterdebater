from django.conf.urls.defaults import *
from tcd.items.models import Topic

# This file is included in tcd.urls with no prefix

urlpatterns = patterns('',
                       # View Topics sorted by highest score
                       (r'^$', 'tcd.items.views.front_page'), 

                       # View Topics sorted by highest score
                       (r'^(?P<sort>(hot))/?$', 'tcd.items.views.topics'), 
                       (r'^(?P<sort>(hot))/(?P<page>\d+)/?$', 'tcd.items.views.topics'),                          

                       # View Topics sorted by submission date
                       (r'^(?P<sort>(new))/?$', 'tcd.items.views.topics'),
                       (r'^(?P<sort>(new))/(?P<page>\d+)/?$', 'tcd.items.views.topics'),
                       
                       # View Comments associated with a topic
                       (r'^(?P<topic_id>\d+)/?$', 'tcd.items.views.comments'),
                       (r'^(?P<topic_id>\d+)/(?P<page>\d+)/?$', 'tcd.items.views.comments'),
                       
                       # Submit a new topic
                       (r'^submit/$', 'tcd.items.views.submit'),
                       
                       # Edit the title, url or description of a topic
                       (r'^edit/(?P<topic_id>\d+)/(?P<page>\d+)/?$', 'tcd.items.views.edit_topic'),

                       # Flag a topic as spam
                       (r'^tflag/$', 'tcd.items.views.tflag'),

                       # Delete a topic
                       (r'^topics/delete/$', 'tcd.items.views.delete_topic'),

                       # Add tags to a topic
                       (r'^topics/addtags/$', 'tcd.items.views.addtags'),

                       # Urls associated with arguments
                       (r'^argue/', include('tcd.items.argue_urls')),

                       )
