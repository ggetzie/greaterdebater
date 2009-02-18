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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template import loader, RequestContext, Context
from django.utils.http import urlquote_plus, urlquote

from forms import CommentForm, DeleteForm
from models import Comment

from tcd.items.models import Topic

import datetime
import pyfo

try:
    COMMENT_REDIRECT_TO=settings.COMMENT_REDIRECT_TO
except AttributeError:
    COMMENT_REDIRECT_TO=''

try:
    COMMENT_SIGNIN_VIEW=settings.COMMENTS_SIGNIN_VIEW
except AttributeError:
    COMMENT_SIGNIN_VIEW=''
    
    
def add(request, topic_id):
    redirect_to='/'
    if request.POST:
        form=CommentForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated():
                request.user.message_set.create(message="Log in to post a comment")
                redirect_to = ''.join(['/login?next=/', str(topic_id)])
            else:		    
                top = get_object_or_404(Topic, pk=topic_id)
                redirect_to = ''.join(['/', str(top.id), '/'])
                params = {'comment': form.cleaned_data['comment'],
                          'user': request.user,
                          'topic': top}
                if form.cleaned_data['toplevel'] == 1:
                    params['parent_id'] = 0
                    params['nesting'] = 10
                else:
                    params['parent_id'] = form.cleaned_data['parent_id']
                    params['nesting'] = form.cleaned_data['nesting'] + 40
                c = Comment(**params)
                c.save()		    
    return HttpResponseRedirect(redirect_to)    
                    
def edit(request, topic_id):
    redirect_to = ''.join(['/', topic_id, '/'])
    if request.POST:
        form=CommentForm(request.POST)
        if form.is_valid():
            c = get_object_or_404(Comment, pk=form.cleaned_data['parent_id'])
            if c.user == request.user:
                c.comment = form.cleaned_data['comment']
                c.save()
    return HttpResponseRedirect(redirect_to)
                                
def delete(request):
    redirect_to = '/'
    if request.POST:
        form=DeleteForm(request.POST)
        if form.is_valid():
            comment = get_object_or_404(Comment, pk=form.cleaned_data['comment_id'])
            redirect_to = form.cleaned_data['referring_page']
            if comment.user == request.user:
                if not comment.arguments.all():

                    if comment.is_removed:
                        comment.is_removed = False

                    else:
                        comment.is_removed = True

                    comment.save()
                    t = loader.get_template('comments/one_comment.html')                
                    c = Context({'comment': comment,
                                 'user': request.user})
                    response = ('response', [('status', 'ok'),
                                             ('id', comment.id),
                                             ('comment', t.render(c))])
                    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
                    return HttpResponse(response)
                else:
                    message="Can't delete a comment that has arguments"            
            else:
                message="Can't delete a comment that isn't yours"
        else:
            message = "Invalid Form"
    else:
        message="Not a POST request"
    response = ('response', [('message', message),
                             ('status', "error"),
                             ('id', comment.id)])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
    return HttpResponse(response)

                                    
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

def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    return render_to_response("comments/comment_detail.html",
                              {'comment': comment},
                              context_instance=RequestContext(request))
                                    
def arguments(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    args_list = comment.arguments.order_by('-start_date')
    return render_to_response("comments/comment_args.html",
                              {'comment': comment,
                               'args_list': args_list},
                              context_instance=RequestContext(request))
                                    
