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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.core.paginator import ObjectPaginator, InvalidPage
from django.template import loader, RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.http import urlquote_plus, urlquote

from forms import CommentForm
from models import Comment

from tcd.items.models import Topic

import datetime

try:
	COMMENT_REDIRECT_TO=settings.COMMENT_REDIRECT_TO
except AttributeError:
	COMMENT_REDIRECT_TO=''

try:
	COMMENT_SIGNIN_VIEW=settings.COMMENTS_SIGNIN_VIEW
except AttributeError:
	COMMENT_SIGNIN_VIEW=''


def add(request, topic_id):
    redirect_to=COMMENT_REDIRECT_TO
    if request.POST:
        form=CommentForm(request.POST)
        if form.is_valid():
#             if 'redirect' in form.cleaned_data:
#                 redirect_to=form.cleaned_data['redirect']
#             else:
#                 redirect_to=COMMENT_REDIRECT_TO

            if not request.user.is_authenticated():
                msg = _("In order to post a comment you should have an account.")
                msg = urlquote_plus(msg)
                if COMMENT_SIGNIN_VIEW:
                    redirect_to=reverse(COMMENT_SIGNIN_VIEW) + "?next=" + redirect_to + "&msg=" + msg
                else:
                    redirect_to='/'
#                 if not request.user.is_authenticated():
#                     return HttpResponseRedirect(redirect_to)
	    else:		    
#             try:    
#                 content_type=ContentType.objects.get(id=form.cleaned_data['content_type'])
#             except:
#                 pass
#             if content_type:		    
		    top = get_object_or_404(Topic, pk=topic_id)
		    redirect_to = reverse('tcd.items.views.comments', args=(topic_id))
		    params = {
		    #'headline':form.cleaned_data['headline'],
		    'comment':form.cleaned_data['comment'],
		    'user':request.user,
		    'pub_date': datetime.datetime.now(),
		    'topic': top
		    #'content_type':content_type,
		    #'object_id':form.cleaned_data['object_id'],
		    }
		    c = Comment(**params)
		    c.save()
    
    return HttpResponseRedirect(redirect_to)    
    
def tip(request):
    from pygments import lexers
    tlexers=lexers.get_all_lexers()
    c = RequestContext(request, {
		'lexers': tlexers,
		
	})

    t = loader.get_template('comments/tipcode.html')
    return HttpResponse(t.render(c))
    
    
def list(request):
    pass
