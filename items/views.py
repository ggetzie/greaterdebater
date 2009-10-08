from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext, Context
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import list_detail

from tcd.comments.forms import ArgueForm, CommentForm, RebutForm
from tcd.comments.models import Comment, tcdMessage, Draw
from tcd.comments.utils import build_list

from tcd.items.forms import tcdTopicSubmitForm, Ballot, Flag, Concession, Response, TagEdit
from tcd.items.models import Topic, Argument, Vote, Tags

from tcd.profiles.forms import tcdLoginForm
from tcd.profiles.models import Profile

from tcd.utils import calc_start


import datetime
import random
import pyfo
import urllib

def comments(request, topic_id, page=1):
    """The view for topic_detail.html 
    Displays the list of comments associated with a topic."""
    paginate_by = 100
    has_previous = False
    has_next = True
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.comment_set.filter(is_msg=False, 
                                      arg_proper=False,
                                      needs_review=False)
    first_c = comments.filter(is_first=True)
    rest_c = build_list(comments.filter(is_first=False).order_by('-pub_date'), 0)
    form_comment = CommentForm()

    if len(rest_c) % paginate_by:
        last_page = (len(rest_c) / paginate_by) + 1
    else:
        last_page = len(rest_c) / paginate_by

    if page == 'last':
        page = last_page
    elif page == 'first':
            page = 1
    else:
        try:
            page = int(page)
        except:
            raise Http404

    start = (page - 1) * paginate_by
    end = page * paginate_by
    previous = page - 1
    next = page + 1

    if start > 0:
        has_previous = True

    try:
        rest_c[end]
    except IndexError:
        has_next = False

    return render_to_response('items/topic_detail.html', 
                              {'object': top,
                               'first_c': first_c,
                               'rest_c': rest_c[start:end],
                               'redirect': ''.join(["/", str(topic_id), "/"]),
                               'has_previous': has_previous,
                               'previous': previous,
                               'has_next': has_next,
                               'next': next,
                               'form_comment': form_comment},
                              context_instance=RequestContext(request)
                              )

def topics(request, page=1, sort="hot"):
    """Display the list of topics on the front page. Order by highest score"""
    paginate_by = 25
    start = calc_start(page, paginate_by, Topic.objects.count())
    user = request.user    

    if sort == "new":
        queryset = Topic.objects.filter(needs_review=False).order_by('-sub_date')
        pager = "new" 
        ttype = "Newest"
    else:
        queryset = Topic.objects.filter(needs_review=False).order_by('-score', '-sub_date')
        pager = "hot" 
        ttype = "Most Active"
    
    return list_detail.object_list(request=request, 
                                   queryset=queryset,
                                   paginate_by=paginate_by, 
                                   page=page,
                                   extra_context={'start': start,
                                                  'page': pager,
                                                  'ttype': ttype})

def front_page(request):
    """Display the home page of GreaterDebater.com, show five hottest arguments and five hottest topics"""
    args = Argument.objects.filter(status__range=(1,2))[0:5]
    topics = Topic.objects.filter(needs_review=False).order_by('-score', '-sub_date')[0:5]

    if request.user.is_authenticated() and tcdMessage.objects.filter(recipient=request.user, is_read=False):        
        request.user.message_set.create(message=''.join(["<a href='/users/u/", request.user.username,
                                                 "/messages/'>You have unread messages</a>"]))
    return render_to_response('items/front_page.html',
                              {'args_list': args,
                               'topic_list': topics},
                              context_instance=RequestContext(request)
                              )

    
    

def tflag(request):    
    top=None
    if request.POST:
        form = Flag(request.POST)
        if form.is_valid():
            top = Topic.objects.get(pk=form.cleaned_data['object_id'])
            user = request.user
            if user in top.tflaggers.all():
                message="You've already flagged this topic"
            else:
                top.tflaggers.add(user)
                if top.tflaggers.count() > 10:
                    top.needs_review = True
                top.save()
                message="Topic flagged"
        else:
            message = "Invalid Form"
    else:
        message = "Not a Post"

    t = loader.get_template('items/msg_div.html')
    if top:
        id = top.id
    else:
        id = 1
    c = Context({'id': id,
                 'message': message,
                 'nesting': "10"})
    response = ('response', [('message', t.render(c))])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)

def delete_topic(request):
    message = "ok"
    status = "fail"
    if request.POST:
        try:
            top = Topic.objects.get(pk=request.POST['topic_id'])
        except MultiValueDictKeyError:
            message = "Invalid Form"
            error_context = Context({'message': message,
                                     'nesting': "10"})
            error_template = loader.get_template('items/msg_div.html')
            response = ('response', [('message', error_template.render(error_context))])
            response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
            return HttpResponse(response)
        if request.user == top.user:
            coms = top.comment_set.filter(is_first=False, is_removed=False)
            if coms:
                message = "Can't delete a topic that has comments"
            else:
                top.delete()
                message = "Topic deleted. FOREVER."
                status = "success"
        else:
            message = "Can't delete a topic that isn't yours"
    else:
        message = "Not a POST"

    c = Context({'message': message,
                 'nesting': "10"})
    t = loader.get_template('items/msg_div.html')
    response = ('response', [('message', t.render(c)),
                             ('status', status)
                             ]
                )
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)

def submit(request):
    """Add a new topic submitted by the user"""
    if request.user.is_authenticated():
        user = request.user.username
        if request.method == 'POST':
            data = request.POST.copy()
            form = tcdTopicSubmitForm(data)
            if form.is_valid():
                try:
                    topic = Topic.objects.get(url=form.cleaned_data['url'])
                    return HttpResponseRedirect(''.join(["/", str(topic.id), "/"]))
                except ObjectDoesNotExist:
                    dtags = form.cleaned_data['tags']
                    tags = '\n'.join([dtags, ','.join(['1']*(dtags.count(',')+1))])
                    topic = Topic(user=request.user,
                                  title=form.cleaned_data['title'],
                                  score=1,
                                  sub_date=datetime.datetime.now(),
                                  comment_length=0,
                                  last_calc=datetime.datetime.now(),
                                  tags = tags
                                  )
                    topic.save()
                    next = ''.join(["/", str(topic.id), "/"])
                    if data['url']:
                        topic.url = form.cleaned_data['url']
                    else:
                        topic.url = next
                    topic.save()
                    utags = Tags(user=request.user, topic=topic, tags=dtags)
                    utags.save()
                    if form.cleaned_data['comment']:
                        comment = Comment(user=request.user,
                                          topic=topic,
                                          pub_date=datetime.datetime.now(),
                                          comment=form.cleaned_data['comment'],
                                          is_first=True,
                                          parent_id=0,
                                          nesting=0)
                        comment.save()
                    return HttpResponseRedirect(next)
        else:
            try:
                form = tcdTopicSubmitForm(initial={'title':request.GET['title'],
                                                   'url':request.GET['url']})
            except MultiValueDictKeyError:
                form = tcdTopicSubmitForm()
                

        return render_to_response("items/submit.html",
                                  {'form': form},
                                  context_instance=RequestContext(request))

    else:        
        
        try:
            # If the user has not logged in but is trying to submit with the bookmarklet
            # keep the url and title from the previous request and forward them after login
            redirect = ''.join([request.path, '?url=', request.GET['url'], 
                                # re-URLEncode the title
                                '&title=', urllib.quote(request.GET['title'].encode('utf-8'))])
        except MultiValueDictKeyError:
            redirect = request.path

        return render_to_response("registration/login.html",
                                  {'redirect': redirect,
                                   'message': "Please log in to submit a topic",
                                   'form': tcdLoginForm()},
                                  context_instance=RequestContext(request))

def edit_topic(request, topic_id, page):
    """Allow the submitter of a topic to edit its title or url"""
    top = get_object_or_404(Topic, pk=topic_id)
    c = Comment.objects.filter(topic=top, is_first=True)
    redirect = ''.join(['/users/u/', request.user.username, '/submissions/', page])    
    if request.method == 'POST':
        if request.user == top.user:
            data = request.POST.copy()
            form = tcdTopicSubmitForm(data)
            if form.is_valid():
                if form.cleaned_data['comment']:
                    if c:
                        c = c[0]
                        c.comment = form.cleaned_data['comment']
                    else:
                        c = Comment(user=top.user,
                                    topic=top,
                                    comment = form.cleaned_data['comment'],
                                    pub_date=datetime.datetime.now(),
                                    is_first=True,
                                    parent_id=0,
                                    nesting=0)
                    c.save()
                top.title = form.cleaned_data['title']            
                top.save()
                return HttpResponseRedirect(redirect)
    else:
        if top.url[0:4] == 'http':
            url = top.url
        else:
            url = ''
        if c:
            comment = c[0].comment
        else:
            comment = ''
        data = {'title': top.title,
                'url': url,
                'comment': comment}
        form = tcdTopicSubmitForm(data)
    return render_to_response("items/edit_topic.html",
                              {'form': form,
                               'username': top.user},
                              context_instance=RequestContext(request))

def addtags(request):
    """A user submits tags to add to a topic"""
    error = True
    if request.POST:
        form = TagEdit(request.POST)
        if form.is_valid():
            user = request.user
            top = get_object_or_404(Topic, pk=form.cleaned_data['topic_id'])
            new_tags = form.cleaned_data['tags']
            current_tags = top.tag_dict(top.tags)
            try:
                current_user_tags = Tags.objects.get(user=user, topic=top)
                cutags = current_user_tags.tags.split(',')
            except ObjectDoesNotExist:
                current_user_tags = Tags(user=user, topic=top, tags='')
                cutags = []
            new_tags = new_tags.split(',')

            # add new tags to the list of tags added by this user
            # and to the list of all tags for this topic
            # don't add to the user's list if it's already in there
            # if it's already in the global list, just increase the count by one
            for tag in new_tags:
                if not tag in cutags:
                    cutags.append(tag)
                    try:
                        current_tags[tag] += 1
                    except KeyError:
                        current_tags[tag] = 1

            current_user_tags.tags = ','.join(cutags)
            current_user_tags.save()

            top.tags = top.tag_string(current_tags)
            top.save()

            t = loader.get_template('items/tag_div.html')
            c = Context({'object': top,
                         'request': request})
            message = t.render(c)
            error = False
        else:
            message = "Invalid Form"
    else:
        message = "Not a Post"

    response = ('response', [('error', error),                                         
                             ('message', message)
                             ])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
    return HttpResponse(response)
    


def challenge(request, c_id):
    """Create a pending argument as one user challenges another."""
    if request.POST:
        form = ArgueForm(request.POST)
        c = get_object_or_404(Comment, pk=c_id)
        defendant = c.user
        redirect = ''.join(['/', str(c.topic_id), '/']) 
        if form.is_valid():
            if not request.user.is_authenticated():
                request.user.message_set.create(message="Log in to start an argument")
            else:
                if Argument.objects.filter(plaintiff=request.user,
                                           comment=c_id):
                    request.user.message_set.create(message="You may only start one argument per comment")
                else:
                    arg = Argument(plaintiff=request.user,
                                   defendant=defendant,
                                   start_date=datetime.datetime.now(),
                                   topic=c.topic,                                   
                                   title=form.cleaned_data['title'],
                                   status=0)
                    arg.save()
                    c.arguments.add(arg)
                    c.save()
                    params = {'comment': form.cleaned_data['comment'],
                              'user': request.user,
                              'topic': c.topic,
                              'parent_id': form.cleaned_data['parent_id'],
                              'nesting': 40,
                              'arg_proper': True}
                    opener = Comment(**params)
                    opener.save()
                    opener.arguments.add(arg)
                    arg.save()
                    msg_txt = ''.join([request.user.username, 
                                       " has challenged you to an argument.\n [Click here](/argue/",
                                       str(arg.id), "/) to view the argument and accept or decline"])
                    msg = tcdMessage(user=request.user,
                                     recipient=defendant,
                                     comment=msg_txt,
                                     subject="Challenge!",
                                     parent_id=0,
                                     nesting=0)
                    msg.save()
                    request.user.message_set.create(message= ''.join(["Challenged ", 
                                                                      arg.defendant.username, 
                                                                      " to an argument"]))
    else:
        request.user.message_set.create(message="Not a POST")
        redirect = '/'
    return HttpResponseRedirect(redirect)

def vote(request):
    """Cast a vote for either the plaintiff or defendant in an argument"""
    message = "ok"
    error = "True"
    if request.POST:        
        form = Ballot(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['argument'])
            voter = get_object_or_404(User, pk=form.cleaned_data['voter'])
            redirect = ''.join(['/argue/', str(arg.id)])
            if voter == request.user:
                vote = Vote(argument=arg,
                            voter=voter,
                            voted_for=form.cleaned_data['voted_for'])
                vote.save()
                arg.calculate_score()
                arg.save()
                all_votes = Vote.objects.filter(argument=arg)
                if vote.voted_for == "P":
                    voted_name = arg.plaintiff.username
                else:
                    voted_name = arg.defendant.username
                
                t = loader.get_template('items/vote_div.html')
                c = Context({'voted_for': voted_name,
                             'pvotes': str(all_votes.filter(voted_for="P").count()),
                             'dvotes': str(all_votes.filter(voted_for="D").count()),
                             'object': arg,
                             'current': True,
                             'request': request})
                message = t.render(c)
                error = "False"
            else:
                message="Can't cast vote as another user"
        else:
            message="Invalid vote"
                
    else:
        message="Not a POST"

    response = ('response', [('error', error),                                         
                             ('message', message)
                             ])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
    return HttpResponse(response)

def unvote(request):
    message = "ok"
    error = True
    if request.POST:
        form = Ballot(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['argument'])
            voter = get_object_or_404(User, pk=form.cleaned_data['voter'])
            redirect = ''.join(['/argue/', str(arg.id)])
            if voter == request.user:
                vote = get_object_or_404(Vote, argument=arg, voter=voter)
                vote.delete()
                error = False
            else:
                message = "Can't delete another user's vote"
        else:
            message = "Invalid Form"
    else:
        message = "Not a Post"
    response = ('response', [('error', error),
                             ('message', message)])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
    return HttpResponse(response)
                                
def rebut(request):
    """Add a new post to an argument."""
    status = "error"
    arg_status = None    
    t = loader.get_template('items/msg_div.html')
    id = "1"
    nesting = "20"

    if request.POST:
        form = RebutForm(request.POST)
        if form.is_valid():            
            arg = get_object_or_404(Argument, pk=form.cleaned_data['arg_id'])
            if arg.whos_up() == request.user:
                if arg.status in (0, 1, 2):
                    if arg.status == 2:
                        arg.status = 1
                    elif arg.status == 1:
                        arg.status = 2
                    elif arg.status == 0:
                        arg.status = 1
                    params = {'comment': form.cleaned_data['comment'],
                      'user': request.user,
                      'topic': arg.topic,
                      'parent_id': form.cleaned_data['parent_id'],
                      'nesting': form.cleaned_data['nesting'] + 40,
                      'arg_proper': True}
                    c = Comment(**params)
                    c.save()
                    arg.comment_set.add(c)
                    arg.save()

                    t = loader.get_template('comments/arg_comment.html')

                    context = Context({'comment': c,
                                       'object': arg})
                    arg_status = ' '.join(["Status:", arg.get_status()])
                    status = "ok"                                 
                else:                   
                    context = Context({'id': id,
                                       'message': "Argument not active!",
                                       'nesting': nesting})                    
            else:
                context = Context({'id': id,
                                   'message': "Not your turn",
                                   'nesting': nesting})                    
        else:
            context = Context({'id': id,
                               'message': "Invalid form - rebut",
                               'nesting': nesting})                    
    else:
        context = Context({'id': id,
                           'message': "Not a POST",            
                           'nesting': nesting})                            

    response = ('response', [('message', t.render(context)),
                             ('status', status),
                             ('arg_status', arg_status)
                             ])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)

def respond(request):
    """Potential opponent accepts or rejects a challenge to an argument."""    
    status = "error"
    turn_actions = ""
    arg_status = "error"
    arg_response = None
    if request.POST:
        form = Response(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['arg_id'])
            if request.user == arg.defendant:
                redirect = ''.join(["/argue/", str(arg.id), "/"])
                if arg.status == 0:
                    response = form.cleaned_data['response']
                    if response == 0:
                        # challenge accepted
                        arg.status = 2
                        arg_response = "accept"
                        message = ''.join([arg.defendant.username, 
                                           " has accepted your challenge. \n[View this argument](", redirect, ")"])
                        msg = tcdMessage(user=request.user,
                                         recipient=arg.plaintiff,
                                         comment=message,
                                         subject="Challenge accepted",
                                         parent_id=0,
                                         pub_date=datetime.datetime.now(),
                                         nesting=0)

                    else:
                        # response == 1, challenge declined
                        # a value other than 0 or 1 would cause the form to not validate
                        arg.status = 6
                        arg_response = "decline"
                        message = ''.join([ arg.defendant.username, 
                                            " has declined your challenge."])
                        msg = tcdMessage(user=request.user,
                                         recipient=arg.plaintiff,
                                         comment=message,
                                         subject="Challenge declined",
                                         parent_id=0,
                                         nesting=0)
                    msg.save()
                    arg.save()
                    status = "ok"
                    ta_template = loader.get_template("items/turn_actions.html")
                    ta_c = Context({'object': arg,
                                    'user': request.user,
                                    'last_c': arg.comment_set.order_by('-pub_date')[0]})
                    turn_actions = ta_template.render(ta_c)
                    response_message = msg.subject
                    arg_status = arg.get_status()
                else:
                    response_message = "Challenge already accepted or declined"
            else:
                response_message = "Can't respond to a challenge that's not for you!"
        else:
            response_message = "Invalid Form"
    else:
        response_message = "Not a POST"

    msg_t = loader.get_template("items/msg_div.html")
    msg_c = Context({'id': "1",
                     'message': response_message,
                     'nesting': "20"})
    responseXML = ('response', [('message', msg_t.render(msg_c)),
                                ('turn_actions', turn_actions),
                                ('arg_response', arg_response),
                                ('arg_status', ": ".join(['Status', arg_status])),
                                ('status', status)])
    responseXML = pyfo.pyfo(responseXML, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(responseXML)


def draw(request):
    """A user offers that the argument be resolved as a draw."""
    status = "error"    
    if request.POST:
        form = RebutForm(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['arg_id'])
            redirect = ''.join(['/argue/', str(arg.id), '/'])
            if arg.whos_up() == request.user and not arg.draw_set.all():
                message = ''.join([request.user.username, 
                                   " has offered a draw regarding argument\n "
                                   "[",  arg.title, "]", "(", redirect, ")",
                                   "\nView the argument to accept or decline."])
                recipient = arg.get_opponent(request.user)
                msg = tcdMessage(user=request.user,
                                 recipient=recipient,
                                 comment=message,
                                 subject="Draw?",
                                 parent_id=0,
                                 nesting=0)
                msg.save()
                draw = Draw(offeror=request.user,
                            recipient=arg.get_opponent(request.user),
                            offer_date=datetime.datetime.now(),
                            argument=arg)
                draw.save()
                return rebut(request)
            else:
                response_message="Not your turn, not your argument, or there's already a draw offer outstanding"
        else:
            response_message = "Invalid Form - draw"
                                    
    else:
        response_message = "Not a POST"
    t = loader.get_template('items/msg_div.html')
    c = Context({'id': "1",
                 'message': response_message,
                 'nesting': "20"})
    response = ('response', [('message', t.render(c)),
                             ('status', status)
                             ])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)


def respond_draw(request):
    """Opponent responds to an offer of a draw"""
    
    # default to error status
    # if the form processes successfully, will be changed to "ok"
    status = "error"
    ta_XML = ""
    arg_status = "error"
    if request.POST:
        form = Response(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['arg_id'])
            draw = get_object_or_404(Draw, argument=arg)
            redirect = ''.join(["/argue/", str(arg.id), "/"])
            if request.user == draw.recipient:
                response = form.cleaned_data['response']
                if response == 0: # draw offer accepted
                    message = ''.join([request.user.username, " has accepted your offer of a draw",
                                       " regarding \n[", arg.title, "](", redirect, ")"])
                    subject = "Draw Accepted"
                    arg.status = 5            
                    response_message = subject
                else: 
                    # response == 1, the draw was declined 
                    # if a value other than 0 or 1, the form would not have validated
                    message = ''.join([request.user.username, " has declined your offer of a draw",
                                       " regarding \n[", arg.title, "](", redirect, ")"])
                    subject = "Draw Declined"
                    response_message = subject
                msg = tcdMessage(user=request.user,
                                     recipient = draw.offeror,
                                     comment = message,
                                     subject = subject,
                                     parent_id = 0,
                                     nesting = 0)
                draw.delete()
                msg.save()
                arg.save()
                ta_template = loader.get_template("items/turn_actions.html")
                ta_c = Context({'object': arg,
                                'user': request.user,
                                'last_c': arg.comment_set.order_by('-pub_date')[0]})
                ta_XML = ta_template.render(ta_c)
                status = "ok"
                arg_status = arg.get_status()
            else:
                response_message = "You can't responsd to this draw offer"                
        else:
            response_message = "Invalid Form"
    else:
        response_message = "Not a POST"
    msg_t = loader.get_template("items/msg_div.html")
    msg_c = Context({'id': "1",
                     'message': response_message,
                     'nesting': "20"})
    responseXML = ('response', [('message', msg_t.render(msg_c)),
                                ('turn_actions', ta_XML),
                                ('arg_status', ": ".join(['Status', arg_status])),
                                ('status', status)])
    responseXML = pyfo.pyfo(responseXML, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(responseXML)

def concede(request):
    """User concedes an argument, opponent wins"""
    status = "error"
    arg_status = None
    if request.POST:
        form = Concession(request.POST)
        if form.is_valid():
            arg = get_object_or_404(Argument, pk=form.cleaned_data['arg_id'])
            user = User.objects.get(pk=form.cleaned_data['user_id'])

            if user == request.user and request.user in (arg.defendant, arg.plaintiff):
                arg.status += 2
                arg.end_date = datetime.datetime.now()
                recipient = arg.get_opponent(request.user)
                prof = Profile.objects.get(user = recipient)
                prof.score += 1
                message = ''.join([request.user.username, " has conceded argument\n", 
                                   "[", arg.title, "]", "(/argue/", str(arg.id), "/)"])
                msg = tcdMessage(user=request.user,
                                 recipient = recipient,
                                 comment = message,
                                 subject = "All right, you win",
                                 parent_id = 0,
                                 nesting = 0)
                msg.save()
                arg.save()
                prof.save()
                response_message = "Point conceded"
                status = "ok"
                arg_status = " ".join(["Status:", arg.get_status()])
            else:
                response_message = "Not your argument"
        else:
            response_message = "Invalid form"
    else: 
        response_message = "Not a Post"

    t = loader.get_template('items/msg_div.html')

    c = Context({'id': "1",
                 'message': response_message,
                 'nesting': "20"})
    response = ('response', [('message', t.render(c)),
                             ('status', status),
                             ('arg_status', arg_status)
                             ])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')    
    return HttpResponse(response)


def arg_detail(request, object_id):
    arg = get_object_or_404(Argument, pk=object_id)
    voted_for = None
    votes = Vote.objects.filter(argument=arg)
    current = False
    new_arg = False
    show_actions = False
    show_votes = False
    show_draw = False
    if request.user.is_authenticated():

        try: 
            vote = votes.get(voter=request.user)
            if vote.voted_for == "P":
                voted_for = arg.plaintiff
            elif vote.voted_for == "D":
                voted_for = arg.defendant
            else:                
                request.user.message_set.create(message="Something funky about your vote")
        except Vote.DoesNotExist:
            pass

    if arg.status in range(0,3):
        current = True

    if request.user == arg.defendant and arg.status == 0:
        new_arg = True

    if current == True and request.user == arg.whos_up() and arg.draw_set.all():
        show_draw = True
        
    if current == True and new_arg == False and not arg.draw_set.all() and request.user == arg.whos_up():
        show_actions = True

    if current == True and request.user.is_authenticated() and not request.user in [arg.plaintiff, arg.defendant]:
        show_votes = True

    if current and (request.user.is_authenticated() == False or request.user == arg.whos_up(invert=1)):
        show_arg_actions = False
    else:
        show_arg_actions = True
                
    last_c = arg.comment_set.order_by('-pub_date')[0]

    return render_to_response("items/arg_detail.html",
                              {'object': arg,
                               'comments': arg.comment_set.order_by('pub_date'),
                               'new_arg': new_arg,
                               'last_c': last_c,
                               'voted_for': voted_for, 
                               'current': current,
                               'pvotes': votes.filter(voted_for="P").count(),
                               'dvotes': votes.filter(voted_for="D").count(), 
                               'show_actions': show_actions,
                               'show_votes': show_votes,
                               'show_arg_actions': show_arg_actions,
                               'show_draw': show_draw
                               },
                              context_instance=RequestContext(request))

def newest_args(request, page=1):
    args = Argument.objects.filter(status__range=(1,2)).order_by('start_date')
    paginate_by = 10
    extra_context = {'start': calc_start(page, paginate_by, args.count())}

    return list_detail.object_list(request=request, queryset=args, paginate_by=paginate_by,page=page,
                                   template_object_name = 'args',
                                   template_name = "items/arg_new.html",)
                                   

def object_list_field(request, model, field, value, sort=None, paginate_by=None, page=None,
                      fv_dict=None, allow_empty=True, template_name=None, 
                      template_loader=loader, extra_context=None, context_processors=None,
                      template_object_name='object', mimetype=None):
    """Extends generic view object_list to display a list of objects filtered 
    by an arbitrary field.
    Works only for fields that are not ForeignKey or ManyToMany. 
    See object_list_foreign_field for ForeignKey fields"""

    if not fv_dict:
        fv_dict = {}
    fv_dict[field] = value
    obj_list = model.objects.filter(**fv_dict)

    if sort:
        obj_list = obj_list.order_by(sort)

    # calculate the number of the first object on this page
    # in case the objects are paginated and want to be displayed as 
    # a numbered list
    extra_context = {'start': calc_start(page, paginate_by, obj_list.count())}

    return list_detail.object_list(request=request, queryset=obj_list, 
                                   paginate_by=paginate_by, page=page, 
                                   allow_empty=allow_empty, template_name=template_name,
                                   template_loader=template_loader, extra_context=extra_context,
                                   context_processors=context_processors,
                                   template_object_name=template_object_name,
                                   mimetype=mimetype)

def object_list_foreign_field(request, model, field, value, foreign_model,
                              foreign_field, fv_dict=None,
                              paginate_by=None, page=None, allow_empty=True,
                              template_name=None, template_loader=loader,
                              extra_context=None, context_processors=None,
                              template_object_name='object', mimetype=None):
    """Generic view to display a list of objects filtered by an arbitary foreign key field"""

    if not fv_dict:
        fv_dict = {}
    foreign_obj = get_object_or_404(foreign_model, **{foreign_field: value})
    fv_dict[field] = foreign_obj.id
    obj_list = model.objects.filter(**fv_dict)

    # calculate the number of the first object on this page
    # in case the objects are paginated and want to be displayed as 
    # a numbered list
    extra_context = {'start': calc_start(page, paginate_by, obj_list.count())}

    return list_detail.object_list(request=request, queryset=obj_list, 
                                   extra_context={foreign_field: foreign_obj},
                                   paginate_by=paginate_by, page=page, 
                                   allow_empty=allow_empty, template_name=template_name,
                                   template_loader=template_loader, 
                                   context_processors=context_processors,
                                   template_object_name=template_object_name,
                                   mimetype=mimetype)




