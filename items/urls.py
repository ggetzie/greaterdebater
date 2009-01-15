from django.conf.urls.defaults import *
from tcd.items.models import Topic

# This file is included in tcd.urls with no prefix

info_dict = {
    'queryset': Topic.objects.all()
    }

urlpatterns = patterns('',
                       (r'^$', 'tcd.items.views.topics'),
                       (r'^page/(?P<page>\d+)/$', 'tcd.items.views.topics'),   
                       (r'^new/$', 'tcd.items.views.new_topics'),                    
                       (r'^new/(?P<page>\d+)/$', 'tcd.items.views.new_topics'),
                       (r'^(?P<topic_id>\d+)/$', 'tcd.items.views.comments'),
                       (r'^(?P<topic_id>\d+)/(?P<page>\d+)$', 'tcd.items.views.comments'),
                       (r'^comments/', include('tcd.comments.urls')),                                              
                       (r'^submit/$', 'tcd.items.views.submit'),
                       (r'^vote/$', 'tcd.items.views.vote'),
                       (r'^edit/(?P<topic_id>\d+)/(?P<page>\d+)$', 'tcd.items.views.edit_topic'),
                       (r'^argue/', include('tcd.items.argue_urls')),
                       (r'^users/', include('tcd.profiles.urls')),
                       (r'^testajax/',  'django.views.generic.simple.direct_to_template', {'template': 'ajax.html'}),
                       (r'^ajax/$', 'tcd.items.views.ajax')
)
