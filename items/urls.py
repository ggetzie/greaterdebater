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
                       (r'^register/$', 'tcd.items.views.register')
)
