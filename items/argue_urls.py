# This url file is included in tcd.items.urls with the prefix 'argue/'
# all views called here in will be passed a user id from the prefix above

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.views.generic import list_detail
from tcd.comments.models import *
from tcd.items.models import *;

arguments = {'queryset': Argument.objects.all()}
    

urlpatterns = patterns('',
                       (r'^(?P<object_id>[\d]+)', 
                        'list_detail.object_detail', 
                        dict(arguments, template_name='/comments/arg_detail.html')),
                       (r'^challenge/(?P<c_id>[\d]+)/$', 
                        'tcd.items.views.challenge'),
                       (r'^(?P<response>[a-z]+)/(?P<a_id>[\d]+)$', 
                        'tcd.items.views.respond'),                       
                       
)
