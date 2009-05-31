# This url file is included in tcd.items.urls with the prefix 'argue/'

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from tcd.comments.models import *
from tcd.items.models import *;

arguments = {'queryset': Argument.objects.all()}

current_args = {'model': Argument,
                'field': 'status__range',
                'value': (1, 2),
                'template_name': "items/arg_current.html",
                'template_object_name': 'args',
                'paginate_by': 10
                }

archive_args = {'model': Argument,
                'field': 'status__range',
                'value': (3, 5),
                'template_name': "items/arg_old.html",
                'template_object_name': 'args',
                'paginate_by': 10
                }
    

urlpatterns = patterns('tcd.items.views',
                       (r'^$', 'object_list_field', current_args),
                       (r'^page/(?P<page>(\d+|last))/$', 'object_list_field', current_args),
                       (r'^archive/$', 'object_list_field', archive_args),
                       (r'^archive/page/(?P<page>(\d+|last))/$', 'object_list_field', archive_args),
                       (r'^challenge/(?P<c_id>[\d]+)/$', 'challenge'),
                       (r'^(?P<object_id>[\d]+)/$', 'arg_detail'),
                       (r'^rebut/$', 'rebut'),
                       (r'^draw/(?P<a_id>[\d]+)/$', 'draw'),  
                       (r'^concede/$', 'concede'),                     
                       (r'^(?P<response>(accept|decline))/(?P<a_id>[\d]+)$', 'respond'),                       
                       (r'^draw/(?P<response>(accept|decline))/(?P<a_id>[\d]+)/$', 'respond_draw'),                                              
)
