# This url file is included in tcd.profiles.urls with the prefix '^(?P<value>[A-Za-z\d]+)/'
# all view functions called below will be passed a parameter named "value" representing
# a username captured from the url.

from django.conf.urls import *
from django.contrib.auth.models import User
from comments.models import TopicComment
from items.models import Topic
from profiles.views import ProfileTopicView, ProfileAllArgs, MessageList, ProfileSavedView, \
    RepliesView, ProfileCommentView


urlpatterns = patterns('',

                       # Display the main profile page, showing the score
                       (r'^$', 'tcd.profiles.views.profile'),
                       (r'^profile/?', 'tcd.profiles.views.profile'),

                       # Display all of the arguments a user has been involved in
                       (r'^arguments/?$', 'tcd.profiles.views.profile_args'),

                       # Display user's arguments for a particular status
                       (r'^arguments/(?P<aset>(pending|current|complete))/?(?P<page>(\d+|last))?/?$', 
                        ProfileAllArgs.as_view(paginate_by=10,
                                               template_name='registration/profile/all_args.html',
                                               context_object_name='args_list')),

                       # Display all of the comments a user has submitted, paginated
                       (r'^comments/?(?P<page>(\d+|last))?/?$', 
                        ProfileCommentView.as_view(paginate_by=25,
                                                   template_name="registration/profile/profile_coms.html",
                                                   context_object_name='comments_list')),

                       # Display all the topics a user has submitted, paginated
                       (r'^submissions/?(?P<page>(\d+|last))?/?$', 
                        ProfileTopicView.as_view(paginate_by=25,
                                                 template_name="registration/profile/profile_tops.html",
                                                 context_object_name='topics_list')),

                       # Display all the topics a user has saved by tagging, paginated
                       (r'^saved/?(page/(?P<page>(\d+|last)))?/?$', 
                        ProfileSavedView.as_view(paginate_by=25,
                                                 template_name="registration/profile/profile_savd.html",
                                                 context_object_name="user_tags_list")),
                                                                                           

                       # Display all the topics a user has tagged with
                       # a particular tag, paginated
                       (r'^saved/(?P<tag>[\w\s\'!@\?\$%#&]+)/?(page/(?P<page>(\d+|last)))?/?$', 
                        ProfileSavedView.as_view(paginate_by=25,
                                                 template_name="registration/profile/profile_savd.html",
                                                 context_object_name="user_tags_list")),


                       # Show all tags associated with a topic for editing
                       (r'^tagedit/(?P<topic_id>\d+)/?$', 'tcd.profiles.views.tagedit'),

                       # Display the body of a message
                       (r'^messages/(?P<object_id>[\d]+)/?$', 'tcd.profiles.views.message_detail'),

                       # Reset the user's password
                       (r'^reset/$', 'tcd.profiles.views.reset_password'), 

                       # Display the reset password page for a user who has forgotten his password
                       # and is following a link with the code sent via email.
                       (r'^reset/(?P<code>[A-Za-z0-9]{32})$', 'tcd.profiles.views.reset_password'), 
)
