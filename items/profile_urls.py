# This url file is included in tcd.items.urls with the prefix '^(?P<user_id>>[A-Za-z\d]+/'
# all views called here in will be passed a user id from the prefix above

from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from tcd.comments.models import *
from tcd.items.models import *;

urlpatterns = patterns('',
                       (r'^$', 'tcd.items.views.profile'),
                       (r'^arguments/$', 'tcd.items.views.profile_args'),
                       (r'^comments/$', 'tcd.items.views.object_list_foreign_field',
                        {'model': Comment,
                         'field': 'user',
                         'foreign_model': User,
                         'foreign_field': 'username',
                         'template_name': "registration/profile/profile_coms.html",
                         'template_object_name': 'comments'
                         }),
                       (r'^submissions/$', 'tcd.items.views.profile_subs'),
)
