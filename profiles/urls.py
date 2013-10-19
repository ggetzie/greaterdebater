# This url file is included in tcd.items.urls with the prefix '^users/'

from django.conf.urls import *
from django.contrib.auth.views import logout
from django.views.generic.base import TemplateView

from profiles.views import MessageList, RepliesView



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

                       # Display messages
                       (r'^messages/?(page/(?P<page>(\d+|last))/?)?$', 
                        MessageList.as_view(paginate_by=25,
                                            template_name="registration/profile/profile_msgs.html",
                                            context_object_name='messages_list')),

                       # Display replies to user's followed topics or comments
                       (r'^replies/?(?P<page>(\d+|last))?/?$', 
                        RepliesView.as_view(paginate_by=25,
                                            template_name="registration/profile/replies.html",
                                            context_object_name="replies_list")),

                       # Display the user's current settings and allow them to be modified
                       (r'^settings/?$', 'tcd.profiles.views.profile_stgs'), 

                       # Urls for displaying differnt parts of users' profiles
                       (r'^u/(?P<value>[A-Za-z\d]+)/', include('tcd.profiles.user_urls')),
                       )

