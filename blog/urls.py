from django.conf.urls.defaults import patterns

# This url file included from tcd.urls with the prefix /blog/

urlpatterns = patterns('',
                       (r'^(?P<user>[A-Za-z\d]+/', 'tcd.blog.views.main'),
                       (r'^(?P<user>[A-Za-z\d]+/', 'tcd.blog.views.main'),
                       )
