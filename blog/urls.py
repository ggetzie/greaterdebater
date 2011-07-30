from django.conf.urls.defaults import patterns
from blog.views import ArchiveView

# This url file included from tcd.urls with the prefix  ^blog/(?P<username>[A-Za-z\d]+)/

urlpatterns = patterns('',
                       
                       # the main page of this blog, shows 5 most recent posts
                       ('^$', 'tcd.blog.views.main'),
                       
                       # a blog post in its entirety
                       (r'^post/(?P<id>[\d]+)/?$', 'tcd.blog.views.post_detail'),

                       # start a new post, for blog author only
                       (r'^new/?$', 'tcd.blog.views.new_post'),

                       # edit a post, whether saved of published
                       (r'^edit/(?P<id>[\d]+)/?$', 'tcd.blog.views.edit_post'),

                       # show posts saved as drafts but not published
                       # author only
                       (r'^drafts/?$', 'tcd.blog.views.show_drafts'),

                       # Show all prevous posts by date, pages
                       (r'^archive/?(?P<page>\d+)?/?$', ArchiveView.as_view(paginate_by = 15,
                                                                            template_name="blogtemplates/archive.html",
                                                                            context_object_name='post_list')),

                       # Show all prevous posts by date, pages
                       (r'^about/?$', 'tcd.blog.views.about'),

                       # Add a comment to a post
                       (r'^addcomment/?$', 'tcd.blog.views.addcomment'),

                       # change post status to draft=False
                       # POST only, AJAX method
                       (r'^publish/?$', 'tcd.blog.views.publish'),

                       # save a post in progress as a draft
                       # POST only, AJAX method
                       (r'^save/?$', 'tcd.blog.views.save_draft'),

                       # save changes and show post HTML
                       # POST only, AJAX method
                       (r'^preview/?$', 'tcd.blog.views.preview'),

                       # Delete a post 
                       # POST only, AJAX method
                       (r'^delete/?$', 'tcd.blog.views.delete')
                       )
