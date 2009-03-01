# This url file is included in tcd.items.urls with the prefix '^users/'

from django.conf.urls.defaults import *
from django.contrib.auth.views import logout





urlpatterns = patterns('',
                       # Login to the website
                       (r'^login/', 'tcd.profiles.views.login'),
                       
                       # Logout of the website
                       (r'^logout/', logout, {'next_page': "/"}),

                       # Register a new account
                       (r'^register/$', 'tcd.profiles.views.register'),

                       # Retrieve a forgotten password
                       (r'^forgot/$', 'tcd.profiles.views.forgot_password'),

                       # Submit feedback via a form
                       (r'^feedback/$', 'tcd.profiles.views.feedback'),

                       # Urls for displaying differnt parts of users' profiles
                       (r'^u/(?P<value>[A-Za-z\d]+)/', include('tcd.profiles.user_urls')),
                       )

