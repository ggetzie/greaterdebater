# This url file is included in tcd.items.urls with the prefix '^users/'

from django.conf.urls.defaults import *
from django.contrib.auth.views import logout
from django.views.generic.base import TemplateView





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

                       # Thank you page for feedback submission
                       (r'^thanks/$', TemplateView.as_view(template_name='registration/thanks.html')),
                       
                       # Check messages
                       (r'^check_messages/$', 'tcd.profiles.views.check_messages'),

                       # Delete private messages
                       (r'^delete_messages/$', 'tcd.profiles.views.delete_messages'),

                       # Delete private messages
                       (r'^delete_current_message/$', 'tcd.profiles.views.delete_current_message'),

                       # Mark reply as read
                       (r'^mark_read/$', 'tcd.profiles.views.mark_read'),

                       # Urls for displaying differnt parts of users' profiles
                       (r'^u/(?P<value>[A-Za-z\d]+)/', include('tcd.profiles.user_urls')),
                       )

