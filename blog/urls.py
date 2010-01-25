from django.conf.urls.defaults import patterns

# This url file included from tcd.urls with the prefix  ^blog/(?P<username>[A-Za-z\d]+)/

urlpatterns = patterns('',
                       
                       # the main page of this blog, shows 5 most recent posts
                       ('^$', 'tcd.blog.views.main'),
                       
                       # a blog post in its entirety
                       (r'^post/(?P<id>[\d]+)/?$', 'tcd.blog.views.post_detail'),

                       # start a new post, for blog author only
                       (r'^edit/?$', 'tcd.blog.views.edit_post'),

                       # edit a post, whether saved of published
                       (r'^edit/(?P<id>[\d]+)/?$', 'tcd.blog.views.edit_post'),

                       # show posts saved as drafts but not published
                       # author only
                       (r'^drafts/?$', 'tcd.blog.views.show_drafts'),

                       # change post status to draft=False
                       # POST only, AJAX method
                       (r'^publish/?$', 'tcd.blog.views.toggle_publish'),

                       # save a post in progress as a draft
                       # POST only, AJAX method
                       (r'^save/?$', 'tcd.blog.views.save_draft')
                       )
