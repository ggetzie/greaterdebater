from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from tcd.items.models import Topic

info_dict = {
    'queryset': Topic.objects.all()
    }

urlpatterns = patterns('',
                       (r'^$', 'django.views.generic.list_detail.object_list', info_dict),
                       (r'^(?P<topic_id>\d+)/$', 'tcd.items.views.comments'),
                       (r'^comments/', include('tcd.comments.urls')),
#                       (r'^(?P<topic_id>\d+)/add/$', 'tcd.items.views.add'),
                       (r'^login/', login),
                       (r'^logout/', logout, {'next_page': "/"})
)
