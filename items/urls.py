from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from items.models import Topic
from items.views import TopicListView, CommentListView, ReviewListView


# This file is included in tcd.urls with no prefix

urlpatterns = patterns('',
                       # Landing page
                       (r'^$', 'tcd.items.views.front_page'), 

                       # View Topics sorted by highest score or submission date
                       (r'^(?P<sort>(hot|new))/(?P<page>(\d+|last))?/?$', TopicListView.as_view(paginate_by=25)),

                       # View Comments associated with a topic
                       (r'^(?P<topic_id>\d+)/(?P<page>(\d+|last))?/?$', CommentListView.as_view(paginate_by=100,
                                                                          template_name='items/topic_detail.html',
                                                                          context_object_name='rest_c')),
                       # Submit a new topic
                       (r'^submit/$', 'tcd.items.views.submit'),

                       # iPhone bookmarklet instructions
                       (r'^iphonebk/?$', TemplateView.as_view(template_name='items/iphonebk.html')),
                       
                       # Edit the title, url or description of a topic
                       (r'^edit/(?P<topic_id>\d+)/(?P<page>\d+)/?$', 'tcd.items.views.edit_topic'),

                       # Flag a topic as spam
                       (r'^tflag/$', 'tcd.items.views.tflag'),

                       # Delete a topic
                       (r'^topics/delete/$', 'tcd.items.views.delete_topic'),

                       # Add tags to a topic
                       (r'^topics/addtags/$', 'tcd.items.views.addtags'),

                       # Delete one tag from a topic
                       (r'^topics/removetag/$', 'tcd.items.views.remove_tag'),

                       # Urls associated with arguments
                       (r'^argue/', include('tcd.items.argue_urls')),

                       # Review topics or comments that might be spam
                       (r'^review/(?P<model>(topic|comment))/(?P<page>\d+)?/?$', 
                        ReviewListView.as_view(paginate_by = 100,
                                               template_name = 'items/review_list.html')),

                       # Decide whether a topic is spam
                       (r'^decide/(?P<model>(topic|comment))/?$', 'items.views.decide'),


                       )
