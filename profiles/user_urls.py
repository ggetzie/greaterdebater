# This url file is included in tcd.profiles.urls with the prefix '^(?P<value>[A-Za-z\d]+)/'
# all view functions called below will be passed a parameter named "value" representing
# a username captured from the url.

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from tcd.comments.models import TopicComment
from tcd.items.models import Topic

comments_dict = {'model': TopicComment,
                 'field': 'user',
                 'fv_dict': {'first': False},                             
                 'foreign_model': User,
                 'foreign_field': 'username',
                 'template_name': "registration/profile/profile_coms.html",
                 'template_object_name': 'comments',
                 'paginate_by': 10}

urlpatterns = patterns('',

                       # Display the main profile page, showing the score
                       (r'^profile/?', 'tcd.profiles.views.profile'),

                       # Display all of the arguments a user has been involved in, paginated
                       (r'^arguments/?$', 'tcd.profiles.views.profile_args'),

                       # Display all of the arguments a user has been involved in, paginated
                       (r'^arguments/(?P<aset>(pending|current|complete))/?$', 
                        'tcd.profiles.views.profile_all_args'),
                       (r'^arguments/(?P<aset>(pending|current|complete))/(?P<page>(\d+|last))/?$', 
                        'tcd.profiles.views.profile_all_args'),

                       # Display all of the comments a user has submitted, paginated
                       (r'^comments/?$', 'tcd.items.views.object_list_foreign_field', 
                        comments_dict),
                       (r'^comments/(?P<page>(\d+|last))/?$', 'tcd.items.views.object_list_foreign_field', 
                        comments_dict),

                       # Display all the topics a user has submitted, paginated
                       (r'^submissions/?$', 'tcd.profiles.views.profile_topics'),
                       (r'^submissions/(?P<page>(\d+|last))/?$', 'tcd.profiles.views.profile_topics'),

                       # Display all the topics a user has saved by tagging, paginated
                       (r'^saved/?$', 'tcd.profiles.views.profile_saved'),
                       (r'^saved/page/(?P<page>(\d+|last))/?$', 'tcd.profiles.views.profile_saved'),

                       # Display all the topics a user has tagged with
                       # a particular tag, paginated
                       (r'^saved/(?P<tag>[\w\s\'!@\?\$%#&]+)/?$', 'tcd.profiles.views.profile_saved'),
                       (r'^saved/(?P<tag>[\w\s\'!@\?\$%#&]+)/page/(?P<page>(\d+|last))/?$', 
                        'tcd.profiles.views.profile_saved'),

                       # Display a list of messages for the user
                       (r'^messages/?$', 'tcd.profiles.views.profile_msgs'), 
                       (r'^messages/page/(?P<page>(\d+|last))/?$', 'tcd.profiles.views.profile_msgs'), 

                       # Display the body of a message
                       (r'^messages/(?P<object_id>[\d]+)$', 'tcd.profiles.views.message_detail'),

                       # Display the user's current settings and allow them to be modified
                       (r'^settings/?$', 'tcd.profiles.views.profile_stgs'), 

                       # Reset the user's password
                       (r'^reset/$', 'tcd.profiles.views.reset_password'), 

                       # Display the reset password page for a user who has forgotten his password
                       # and is following a link with the code sent via email.
                       (r'^reset/(?P<code>[A-Za-z0-9]{32})$', 'tcd.profiles.views.reset_password'), 
)
