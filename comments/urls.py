
from django.conf.urls.defaults import patterns
from comments.views import CommentDebateList

# This url file is included from items.urls with the prefix /comments/

urlpatterns = patterns('',

                       # Why is this here?
                       (r'^$', 'comments.views.list'),

                       # Add a comment to a topic
                       (r'^(?P<topic_id>\d+)/add/$', 'comments.views.add'),

                       # Edit a comment
                       (r'^(?P<topic_id>\d+)/edit/$', 'comments.views.edit'),

                       # View a single comment on a page by itself
                       (r'^(?P<comment_id>\d+)/?$', 'comments.views.comment_detail'),

                       # Delete a comment
                       (r'[delete|undelete]/$', 'comments.views.delete'),

                       # View all arguments associated with a comment
                       (r'^(?P<comment_id>\d+)/arguments/?(?P<page>\d+)?/?$', 
                        CommentDebateList.as_view(paginate_by=10,
                                                  template_name='comments/comment_args.html',
                                                  context_object_name='args_list')),

                       # Flag a comment as spam
                       (r'^flag/$', 'comments.views.flag'),

                       # Follow or unfollow a topic or comment for
                       # updates when new replies are made
                       (r'^follow/$', 'comments.views.toggle_follow'),
                       )
