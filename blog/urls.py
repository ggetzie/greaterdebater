from django.conf.urls.defaults import patterns

# This url file included from tcd.urls with the prefix /blog/

urlpatterns = patterns(r'^(?P<user>[A-Za-z\d]+/',
                       ('', 'tcd.blog.views.main'),
                       (r'post/(?P<id>[\d]+/?', 'tcd.blog.views.post_detail'),
                       (r'post/new/?', 'tcd.blog.views.post_new'),
                       )
