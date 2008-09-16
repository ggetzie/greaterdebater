# This url file is included in tcd.items.urls with the prefix '^(?P<value>>[A-Za-z\d]+/'
# all views called here in will be passed a user id from the prefix above

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from tcd.comments.models import *
from tcd.items.models import *;

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
                       (r'^$', 'tcd.items.views.profile'),
                       (r'^arguments/$', 'tcd.items.views.profile_args'),
                       (r'^arguments/(?P<page>\d+)$', 'tcd.items.views.profile_args'),
                       (r'^comments/$', 'tcd.items.views.object_list_foreign_field', 
                        comments_dict),
                       (r'^comments/(?P<page>\d+)$', 'tcd.items.views.object_list_foreign_field', 
                        comments_dict),
                       (r'^submissions/$', 'tcd.items.views.object_list_foreign_field', 
                        submissions_dict),
                       (r'^submissions/(?P<page>\d+)$', 'tcd.items.views.object_list_foreign_field', 
                        submissions_dict),
                       (r'^messages/$', 'tcd.items.views.profile_msgs'), 
                       (r'^messages/(?P<object_id>[\d]+)$', 'tcd.items.views.message_detail'),
                       (r'^settings/$', 'tcd.items.views.profile_stgs'), 
                       (r'^reset/$', 'tcd.items.views.reset_password'), 
)
