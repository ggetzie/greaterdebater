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
                       ('^$', 'comments.views.list'),
                       ('^(?P<topic_id>\d+)/add/$', 'comments.views.add'),
                       ('^(?P<topic_id>\d+)/edit/$', 'comments.views.edit'),
                       ('^(?P<comment_id>\d+)/$', 'comments.views.comment_detail'),
                       ('[delete|undelete]/$', 'comments.views.delete'),
                       ('^(?P<comment_id>\d+)/arguments/$', 'comments.views.arguments'),                        
                       )
