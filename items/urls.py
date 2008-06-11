from django.conf.urls.defaults import *
from django.contrib.auth.views import logout
from tcd.items.models import Topic


info_dict = {
    'queryset': Topic.objects.all()
    }

urlpatterns = patterns('',
                       (r'^$', 'tcd.items.views.topics'),
#                       (r'^$', 'django.views.generic.list_detail.object_list', info_dict),
                       (r'^(?P<topic_id>\d+)/$', 'tcd.items.views.comments'),
                       (r'^comments/', include('tcd.comments.urls')),                       
                       (r'^login/', 'tcd.items.views.login'),
                       (r'^logout/', logout, {'next_page': "/"}),
                       (r'^register/$', 'tcd.items.views.register'),
                       (r'^submit/$', 'tcd.items.views.submit'),
                       (r'^(?P<username>[A-Za-z\d]+)/', include('tcd.items.profile_urls')),
                       (r'^argue/challenge/(?P<df_id>[A-Za-z\d]+)/(?P<c_id>\d+)/$', 'tcd.items.views.challenge'),
#                       (r'^argue/accept/(?P<arg_id>\d+)$', 'tcd.items.views.accept'),                       
#                       (r'^argue/decline/(?P<pl_id>)[A-Za-z\d]+$', 'tcd.items.views.decline'),                       
)
