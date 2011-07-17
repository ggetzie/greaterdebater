# This url file is included in tcd.items.urls with the prefix 'argue/'

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from items.views import DebateListView

urlpatterns = patterns('tcd.items.views',
                       
                       # Display a list of arguments:
                       # new = current arguments sorted by date
                       # hot = current arguments sorted by score
                       # archive = completed arguments sorted by date
                       (r'^(?P<sort>(new|hot|archive))/(page/)?(?P<page>(\d+|last))?/?$', 
                        DebateListView.as_view(template_name='items/arg_main.html',
                                               context_object_name='args_list',
                                               paginate_by=25)),

                       # Challenge a user to an argument
                       (r'^challenge/(?P<c_id>[\d]+)/$', 'challenge'),
                       
                       # Display a single argument
                       (r'^(?P<object_id>[\d]+)/?$', 'arg_detail'),

                       # POST a rebuttal to an argument
                       (r'^rebut/$', 'rebut'),

                       # POST an offer to call an argument a draw
                       (r'^draw/$', 'draw'),  
                       
                       # Respond to an offer to call an argument a draw
                       (r'^draw/respond/$', 'respond_draw'),                                              

                       # Concede an argument
                       (r'^concede/$', 'concede'),                     

                       # Respond to a challenge for an argument
                       (r'^respond/$', 'respond'),          
                                  
                       # Vote for a participant in an argument
                       (r'^vote/$', 'vote'),

                       # Vote for a participant in an argument
                       (r'^unvote/$', 'unvote'),
)
