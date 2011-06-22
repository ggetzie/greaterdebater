# This url file is included in tcd.urls with the prefix '^omsr/'

from django.conf.urls.defaults import *
from django.contrib.auth.views import logout

urlpatterns = patterns('',
                       # Login to the website
                       (r'', 'tcd.omsr.views.tweets'),
                       
                       )

