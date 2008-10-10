# This url file is included in tcd.items.urls with the prefix '^users/'

from django.conf.urls.defaults import *
from django.contrib.auth.views import logout





urlpatterns = patterns('',
                       (r'^login/', 'tcd.profiles.views.login'),
                       (r'^logout/', logout, {'next_page': "/"}),                       
                       (r'^register/$', 'tcd.profiles.views.register'),
                       (r'^u/(?P<value>[A-Za-z\d]+)/', include('tcd.profiles.user_urls')),
                       )

