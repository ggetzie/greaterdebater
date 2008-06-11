# This url file is included in tcd.items.urls with the prefix '^(?P<user_id>>[A-Za-z\d]+/'
# all views called here in will be passed a user id from the prefix above

from django.conf.urls.defaults import *


urlpatterns = patterns('',
                       (r'^$', 'tcd.items.views.profile'),
                       (r'^arguments/$', 'tcd.items.views.profile_args'),
)
