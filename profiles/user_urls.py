# This url file is included in tcd.profiles.urls with the prefix '^(?P<value>[A-Za-z\d]+)/'
# all view functions called below will be passed a parameter named "value" representing
# a username captured from the url.

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from tcd.comments.models import Comment
from tcd.items.models import Topic

comments_dict = {'model': Comment,
                 'field': 'user',
                 'fv_dict': {'is_msg': False,
                             'is_first': False,
                             'arg_proper': False,},
                 'foreign_model': User,
                 'foreign_field': 'username',
                 'template_name': "registration/profile/profile_coms.html",
                 'template_object_name': 'comments',
                 'paginate_by': 3}

submissions_dict = {'model': Topic,
                    'field': 'user',
                    'foreign_model': User,
                    'foreign_field': 'username',
                    'template_name': "registration/profile/profile_tops.html",
                    'template_object_name': 'topics',
                    'paginate_by': 3}

urlpatterns = patterns('',
                        (r'^profile/', 'tcd.profiles.views.profile'),
                        (r'^arguments/$', 'tcd.profiles.views.profile_args'),
                        (r'^arguments/(?P<page>\d+)$', 'tcd.profiles.views.profile_args'),
                        (r'^comments/$', 'tcd.items.views.object_list_foreign_field', 
                         comments_dict),
                        (r'^comments/(?P<page>\d+)$', 'tcd.items.views.object_list_foreign_field', 
                         comments_dict),
                        (r'^submissions/$', 'tcd.items.views.object_list_foreign_field', 
                         submissions_dict),
                        (r'^submissions/(?P<page>\d+)$', 'tcd.items.views.object_list_foreign_field', 
                         submissions_dict),
                        (r'^messages/$', 'tcd.profiles.views.profile_msgs'), 
                        (r'^messages/(?P<object_id>[\d]+)$', 'tcd.profiles.views.message_detail'),
                        (r'^settings/$', 'tcd.profiles.views.profile_stgs'), 
                        (r'^reset/$', 'tcd.profiles.views.reset_password'), 
                        (r'^reset/(?P<code>[A-Za-z0-9]{32})$', 'tcd.profiles.views.reset_password'), 
)
