# This url file is included in tcd.items.urls with the prefix 'argue/'

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
# from tcd.comments.models import *
from tcd.items.models import Argument;

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
                'paginate_by': 10,
                'sort': '-start_date'
                }
    

urlpatterns = patterns('tcd.items.views',
                       # Display active arguments, sorted by score
                       (r'^$', 'object_list_field', current_args),
                       (r'^page/(?P<page>(\d+|last))/?$', 'object_list_field', current_args),

                       # Display active arguments, sorted by date
                       (r'^new/$', 'newest_args'),
                       (r'^new/page/(?P<page>(\d+|last))/?$', 'newest_args'),

                       # Display completed arguments
                       (r'^archive/$', 'object_list_field', archive_args),
                       (r'^archive/page/(?P<page>(\d+|last))/$', 'object_list_field', archive_args),

                       # Challenge a user to an argument
                       (r'^challenge/(?P<c_id>[\d]+)/$', 'challenge'),
                       
                       # Display a single argument
                       (r'^(?P<object_id>[\d]+)/$', 'arg_detail'),

                       # POST a rebuttal to an argument
                       (r'^rebut/$', 'rebut'),

                       # POST an offer to call an argument a draw
                       (r'^draw/$', 'draw'),  
                       
                       # Responsd to an offer to call an argument a draw
                       (r'^draw/respond/$', 'respond_draw'),                                              
                       (r'^draw/(?P<response>(accept|decline))/(?P<a_id>[\d]+)/$', 'respond_draw'),       

                       # Concede an argument
                       (r'^concede/$', 'concede'),                     

                       # Respond to a challenge for an argument
                       (r'^respond/$', 'respond'),          
                                  
                       # Vote for a participant in an argument
                       (r'^vote/$', 'vote'),

                       # Vote for a participant in an argument
                       (r'^unvote/$', 'unvote'),
)
