from django.conf.urls.defaults import *
from django.contrib.auth.views import logout
from tcd.items.models import Topic


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
                       (r'^login/', 'tcd.items.views.login'),
                       (r'^logout/', logout, {'next_page': "/"}),
                       (r'^register/$', 'tcd.items.views.register'),
                       (r'^submit/$', 'tcd.items.views.submit'),
                       (r'^edit/(?P<topic_id>\d+)/$', 'tcd.items.views.edit_topic'),
                       (r'^argue/', include('tcd.items.argue_urls')),
                       (r'^(?P<value>[A-Za-z\d]+)/', include('tcd.items.profile_urls')),
)
