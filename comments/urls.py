# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 Benoit Chesneau <benoitc@metavers.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.conf.urls.defaults import patterns

# This url file is included from items.urls with the prefix /comments/

urlpatterns = patterns('',

                       # Why is this here?
                       (r'^$', 'comments.views.list'),

                       # Add a comment to a topic
                       (r'^(?P<topic_id>\d+)/add/$', 'comments.views.add'),

                       # Edit a comment
                       (r'^(?P<topic_id>\d+)/edit/$', 'comments.views.edit'),

                       # View a single comment on a page by itself
                       (r'^(?P<comment_id>\d+)/$', 'comments.views.comment_detail'),

                       # Delete a comment
                       (r'[delete|undelete]/$', 'comments.views.delete'),

                       # View all arguments associated with a comment
                       (r'^(?P<comment_id>\d+)/arguments/$', 'comments.views.arguments'),                        
                       (r'^(?P<comment_id>\d+)/arguments/(?P<page>\d+)/?$', 'comments.views.arguments'),                        

                       # Flag a comment as spam
                       (r'^flag/$', 'comments.views.flag'),
                       )
