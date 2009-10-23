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
from django.contrib.auth.models import User
from django.template import loader, RequestContext, Context
from django.utils.http import urlquote_plus, urlquote
from django.views.generic import list_detail

from forms import CommentForm, DeleteForm
from models import Comment

from tcd.items.models import Topic
from tcd.items.forms import Flag

from tcd.utils import calc_start

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
    redirect_to = ''.join(['/', topic_id, '/'])
    if request.POST:
        form=CommentForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated():
                request.user.message_set.create(message="Please log in to post a comment")
                redirect_to = ''.join(['/login?next=/', str(topic_id), '/'])
            else:		    
                top = get_object_or_404(Topic, pk=topic_id)
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
        else:
            message = "<p>Oops! A problem occurred.</p>"
            request.user.message_set.create(message=message+str(form.errors))
    return HttpResponseRedirect(redirect_to)    
                    
def edit(request, topic_id):
    redirect_to = ''.join(['/', topic_id, '/'])
    if request.POST:
        form=CommentForm(request.POST)
        if form.is_valid():
            c = get_object_or_404(Comment, pk=form.cleaned_data['parent_id'])
            if c.user == request.user:
                c.comment = form.cleaned_data['comment']
                c.comment += "\n\n*Edited: %s*" % datetime.datetime.now().strftime("%H:%M on %b-%d-%Y")
                c.save()
        else:
            message = "<p>Oops! A problem occurred.</p>"
            request.user.message_set.create(message=message+str(form.errors))
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
    msg_template = loader.get_template('items/msg_div.html')
    msg_context = Context({'id': comment.id,
                          'message': message,
                          'nesting': comment.nesting})
    response = ('response', [('message', msg_template.render(msg_context)),
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
                                    
def arguments(request, comment_id, page=1):
    paginate_by = 10
    comment = get_object_or_404(Comment, pk=comment_id)
    args_list = comment.arguments.filter(status__range=(1,5)).order_by('-start_date')
    start = calc_start(page, paginate_by, args_list.count())

    return list_detail.object_list(request=request,
                                   queryset=args_list,
                                   page=page,
                                   paginate_by=paginate_by,
                                   extra_context={'start': start,
                                                  'comment': comment},
                                   template_name="comments/comment_args.html",
                                   template_object_name="args")
                                    
def flag(request):
    if request.POST:
        form = Flag(request.POST)
        if form.is_valid():
            com = Comment.objects.get(pk=form.cleaned_data['object_id'])
            user = request.user
            if user in com.cflaggers.all():
                message="You've already flagged this comment"
            else:
                com.cflaggers.add(user)
                if com.cflaggers.count() > 10 or user.is_staff:
                    com.needs_review = True
                com.save()
                message="Comment flagged"
        else:
            message = "Invalid Form"
    else:
        message = "Not a Post"

    t = loader.get_template('items/msg_div.html')
    c = Context({'id': com.id,
                 'message': message,
                 'nesting': com.nesting})
    response = ('response', [('message', t.render(c))])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)
