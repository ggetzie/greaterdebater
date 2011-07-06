from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import models
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext, Context
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import list_detail

from comments.forms import ArgueForm, CommentForm, RebutForm
from comments.models import TopicComment, ArgComment, nVote, Debate, tcdMessage, Draw, \
    fcomMessage
from comments.utils import build_list

from items.forms import tcdTopicSubmitForm, Ballot, Flag, Concession, Response, TagEdit, \
    TagRemove, DecideForm
from items.models import Topic, Tags

from profiles.forms import tcdLoginForm, tcdUserCreationForm
from profiles.models import Profile

from settings import HOSTNAME

from tcd.utils import calc_start, tag_dict, tag_string, update_tags, render_to_AJAX, render_message


import datetime
import random
import pyfo
import urllib

models={'comment': TopicComment,
        'topic':  Topic}

def comments(request, topic_id, page=1):
    """The view for topic_detail.html 
    Displays the list of comments associated with a topic."""
    paginate_by = 100
    has_previous = False
    has_next = True
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.topiccomment_set.filter(first=False,
                                           needs_review=False,
                                           spam=False)
    rest_c = build_list(comments.order_by('-pub_date'), 0)
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

    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False

    if top.tags:
        keywords = ", ".join(top.tags.split('\n')[0].split(','))
    else:
        keywords = "greaterdebater, debate, comment, topic"

    return render_to_response('items/topic_detail.html', 
                              {'object': top,                               
                               'rest_c': rest_c[start:end],
                               'redirect': ''.join(["/", str(topic_id), "/"]),
                               'has_previous': has_previous,
                               'previous': previous,
                               'has_next': has_next,
                               'next': next,
                               'form_comment': form_comment,
                               'newwin': newwin,
                               'keywords': keywords},
                              context_instance=RequestContext(request)
                              )

def topics(request, page=1, sort="hot"):
    """Display the list of topics. Order by highest score (hot) or most recent (new)"""
    paginate_by = 25
    start = calc_start(page, paginate_by, Topic.objects.count())

    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False
    queryset = Topic.objects.filter(needs_review=False, spam=False)
    if sort == "new":
        queryset = queryset.order_by('-sub_date')
        pager = "new" 
        ttype = "Newest"
    else:
        queryset = queryset.order_by('-score', '-sub_date')
        pager = "hot" 
        ttype = "Most Active"
    
    return list_detail.object_list(request=request, 
                                   queryset=queryset,
                                   paginate_by=paginate_by, 
                                   page=page,
                                   extra_context={'start': start,
                                                  'page': pager,
                                                  'ttype': ttype,
                                                  'newwin': newwin,
                                                  'source': 0,
                                                  })

def front_page(request):
    """Display the home page of GreaterDebater.com, show five hottest arguments and 25 hottest topics"""
    args = Debate.objects.filter(status__in=range(1,6)).order_by('-start_date')[:5]
    topics = Topic.objects.filter(needs_review=False, spam=False).order_by('-score', '-sub_date')[:25]

    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False
        
    return render_to_response('items/front_page.html',
                              {'args_list': args,
                               'topic_list': topics,
                               'newwin': newwin,
                               'source': 0},
                              context_instance=RequestContext(request)
                              )

def tflag(request):    
    
    if not request.user.is_authenticated():
        message = render_message("Not logged in", 10)
        return render_to_AJAX(status="error",
                              messages=[message])
    if not request.POST:
        message = render_message("Not a POST", 10)
        return render_to_AJAX(status="error",
                              messages=[message])

    form = Flag(request.POST)
    if not form.is_valid():
        message = render_message("Invalid Form", 10)
        return render_to_AJAX(status="error",
                              messages=[message])

    try:
        top = Topic.objects.get(pk=form.cleaned_data['object_id'])
    except Topic.DoesNotExist:
        message = render_message("Topic not found", 10)
        return render_to_AJAX(status="alert",
                              messages=[message])
    user = request.user
    if user in top.tflaggers.all():
        message="You've already flagged this topic"
    else:                
        top.tflaggers.add(user)
        if top.tflaggers.count() > 10 or user.is_staff:
            top.needs_review = True
            prof = Profile.objects.get(user=top.user)
            prof.rate=10
            prof.save()
        top.save()
        message="Topic flagged"

    return render_to_AJAX(status="ok",
                          messages=[render_message(message, 10)])

def delete_topic(request):
    
    if not request.POST:
        message = render_message("Not a POST", 10)
        return render_to_AJAX(status="error", messages=[message])
    
    try:
        top = Topic.objects.get(pk=request.POST['topic_id'])
    except Topic.DoesNotExist:
        message = render_message("Topic not found", 10)
        return render_to_AJAX(status="alert", messages=[message])
    except MultiValueDictKeyError:
        message = render_message("Invalid Form", 10)
        return render_to_AJAX(status="alert", messages=[message])

    if not request.user == top.user:
        message = render_message("Can't delete a topic that isn't yours", 10)
        return render_to_AJAX(status="alert", messages=[message])


    coms = top.topiccomment_set.filter(first=False, removed=False,
                                       needs_review=False, spam=False)
    if coms:
        message = render_message("Can't delete a topic that has comments", 10)
        return render_to_AJAX(status="error", messages=[message])

    top.delete()
    message = render_message("Topic deleted. FOREVER.", 10)
    return render_to_AJAX(status="ok", messages=[message])


def submit(request):
    """Add a new topic submitted by the user"""

    # Look for a url being submitted, if there's already
    # a topic that has it, redirect to that topic
    try:
        topic = Topic.objects.get(url=request.GET['url'])
        return HttpResponseRedirect("/" + str(topic.id) + "/")
    except (MultiValueDictKeyError, Topic.DoesNotExist):
        pass

    if not request.user.is_authenticated():
        
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
                                   'message': "Please log in or create an account to continue submitting your topic",
                                   'form': tcdLoginForm(),
                                   'rform': tcdUserCreationForm()},
                                  context_instance=RequestContext(request))

    user = request.user.username
    if not request.method == 'POST':
        try:
            form = tcdTopicSubmitForm(initial={'title':request.GET['title'],
                                               'url':request.GET['url']})
        except MultiValueDictKeyError:
            form = tcdTopicSubmitForm()

        return render_to_response("items/submit.html",
                                  {'form': form},
                                  context_instance=RequestContext(request))

    data = request.POST.copy()
    form = tcdTopicSubmitForm(data)
    if not form.is_valid():
        return render_to_response("items/submit.html",
                                  {'form': form},
                                  context_instance=RequestContext(request))

    prof = get_object_or_404(Profile, user=request.user)

    if prof.probation:
        next = '/'
        prevtop = Topic.objects.filter(user=request.user, needs_review=True, spam=False)
        if prevtop:
            message = "Your previous topic is still awaiting review. <br />" + \
                "Please wait until it has been approved before submitting another topic."
            messages.info(request, message)
            return HttpResponseRedirect(next)

    try:
        # If the topic already exists, redirect to it
        topic = Topic.objects.get(url=form.cleaned_data['url'])
        return HttpResponseRedirect("/" + str(topic.id) + "/")
    except ObjectDoesNotExist:
        # Make sure the user is not submitting too fast
        ratemsg = prof.check_rate()
        if ratemsg:
            messages.info(request, ratemsg)
            return HttpResponseRedirect(request.path)

        topic = Topic(user=request.user,
                      title=form.cleaned_data['title'],
                      score=1,
                      sub_date=datetime.datetime.now(),
                      comment_length=0,
                      last_calc=datetime.datetime.now(),
                      needs_review=prof.probation
                      )
        topic.save()

        if prof.probation:
            next = '/'
            messages.info(request, "Thank you! Your topic will appear after a brief review.")
        else:
            next = "/" + str(topic.id) + "/"

        if data['url']:
            topic.url = form.cleaned_data['url']
        else:
            topic.url = HOSTNAME + '/' + str(topic.id) + '/'

        dtags = form.cleaned_data['tags']
        if dtags:
            # create the count of all tags for the topic
            tags = '\n'.join([dtags, ','.join(['1']*(dtags.count(',')+1))])
            topic.tags = tags

            # create a Tags object to indicate the submitter
            # added these tags to this topic                        
            utags = Tags(user=request.user, topic=topic, tags=dtags)
            utags.save()

            # update the count of all tags used by the submitter
            prof = Profile.objects.get(user=request.user)
            prof.tags = update_tags(prof.tags, dtags.split(','))
            prof.save()

        topic.save()

        prof.last_post = topic.sub_date
        prof.save()

        if prof.followtops:
            topic.followers.add(request.user)
            topic.save()

        if form.cleaned_data['comment']:
            comment = TopicComment(user=request.user,
                                   ntopic=topic,
                                   pub_date=datetime.datetime.now(),
                                   comment=form.cleaned_data['comment'],
                                   first=True,
                                   nparent_id=0,
                                   nnesting=0)
            comment.save()

            topic.comment_length += len(comment.comment)
            topic.recalculate()
            topic.save()
        return HttpResponseRedirect(next)


def edit_topic(request, topic_id, page):
    """Allow the submitter of a topic to edit its title or url"""
    top = get_object_or_404(Topic, pk=topic_id)
    c = TopicComment.objects.filter(ntopic=top, first=True)
    redirect = '/users/u/' + request.user.username + '/submissions/' + page
    if not request.user == top.user:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

    if request.method == 'POST':
        if request.user == top.user:
            data = request.POST.copy()
            form = tcdTopicSubmitForm(data)
            if form.is_valid():
                if form.cleaned_data['comment']:
                    if c:
                        c = c[0]
                        oldlen = len(c.comment)
                        c.comment = form.cleaned_data['comment']
                    else:
                        oldlen = 0
                        c = TopicComment(user=top.user,
                                         ntopic=top,
                                         comment = form.cleaned_data['comment'],
                                         pub_date=datetime.datetime.now(),
                                         first=True,
                                         nparent_id=0,
                                         nnesting=0)                    
                    c.save()

                    top.comment_length += len(c.comment) - oldlen
                    top.recalculate()
                    top.save()
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

    if not request.user.is_authenticated():
        message = render_message("Not logged in", 10)
        return render_to_AJAX(status='error',
                              messages=[message])

    if not request.POST:
        return render_to_AJAX(status='error',
                              messages=["Not a POST"])
    
    form = TagEdit(request.POST)
    if not form.is_valid():
        message = render_message(str(form['tags'].errors), 10)
        return render_to_AJAX(status='error',
                              messages=[message])

    user = request.user
    prof = get_object_or_404(Profile, user=user)
    top = get_object_or_404(Topic, pk=form.cleaned_data['topic_id'])
    source = form.cleaned_data['source']

    new_tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
    unique_tags = []
    try:
        current_user_tags = Tags.objects.get(user=user, topic=top)
        cutags = current_user_tags.tags.split(',')
    except ObjectDoesNotExist:
        current_user_tags = Tags(user=user, topic=top, tags='')
        cutags = []

    # don't let a user add a particular tag to a particular
    # topic more than once
    for tag in new_tags:
        if not tag in cutags:
            cutags.append(tag)
            unique_tags.append(tag)

    current_user_tags.tags = ','.join(cutags)
    current_user_tags.save()

    top.tags = update_tags(top.tags, unique_tags)
    top.save()

    prof.tags = update_tags(prof.tags, unique_tags)
    prof.save()

    if source == 1:
        utags = Tags.objects.get(user=prof.user, topic=top)
        tagload = loader.get_template('items/tag_div_user.html')
        tagcontext = Context({'object': utags,
                               'source': source,
                              'request': request})
    else:
        tagload = loader.get_template('items/tag_div.html')            
        tagcontext = Context({'object': top,
                              'source': source,
                              'request': request})
    tagdiv = tagload.render(tagcontext)

    # c = Context({'message': message,
    #              'id': request.POST['topic_id'],
    #              'fsize': 'font-size: small;',
    #              'nesting': "10"})
    # t = loader.get_template('items/msg_div.html')
    
    return render_to_AJAX(status='ok',
                          messages=[tagdiv])

def remove_tag(request):

    if not request.POST:
        message = render_message("Not a POST", 10)
        return render_to_AJAX(status="error", messages=[message])
    
    if not request.user.is_authenticated():
        message = render_message("Not logged in", 10)
        return render_to_AJAX(status="error", messages=[message])

    form = TagRemove(request.POST)
    
    if not form.is_valid():
        return render_to_AJAX(status="alert",
                              messages=["Invalid Form"])

    try:
        prof = Profile.objects.get(user__id=form.cleaned_data['user_id'])
        if not prof.user == request.user:
            message = render_message("Can't remove another user's tag", 10)
            return render_to_AJAX(status="error", messages=[message])

        topic = Topic.objects.get(pk=form.cleaned_data['topic_id'])
        tags = Tags.objects.get(topic=topic, user=prof.user)
        tag = form.cleaned_data['tag']

        topic_dict = tag_dict(topic.tags)
        if topic_dict[tag] == 1:
            del topic_dict[tag]
        else:
            topic_dict[tag] -= 1
        topic.tags = tag_string(topic_dict)
        topic.save()

        prof_dict = tag_dict(prof.tags)
        if prof_dict[tag] == 1:
            del prof_dict[tag]
        else:
            prof_dict[tag] -= 1
        prof.tags = tag_string(prof_dict)
        prof.save()

        tags_list = tags.tags.split(',')
        tags_list.remove(tag)
        if tags_list:
            tags.tags = ','.join(tags_list)
            tags.save()
        else:
            tags.delete()

        msg = render_message("Tag removed", 10)
        return render_to_AJAX(status="ok",
                              messages=[msg])

    except ObjectDoesNotExist:
        msg = "Invalid topic, user or tag"
        return render_to_AJAX(status="alert",
                              messages=[msg])


def challenge(request, c_id):
    """Create a pending argument as one user challenges another."""
    redirect = '/'
    if not request.POST:
        messages.warning(request, "Not a POST")
        return HttpResponseRedirect(redirect)


    form = ArgueForm(request.POST)
    c = get_object_or_404(TopicComment, pk=c_id)
    defendant = c.user
    redirect = '/' + str(c.ntopic.id) + '/'

    if not form.is_valid():
        message = "<p>Oops! A problem occurred.</p>"
        messages.error(request, message + str(form.errors))
        return HttpResponseRedirect(redirect)


    if not request.user.is_authenticated():
        messages.warning(request, "Please log in to start a debate")
        return HttpResponseRedirect(redirect)

    if Debate.objects.filter(plaintiff=request.user,
                               incite=c):
        messages.warning(request, "You may only start one debate per comment")
        return HttpResponseRedirect(redirect)

    arg = Debate(plaintiff=request.user,
                 defendant=defendant,
                 start_date=datetime.datetime.now(),
                 topic=c.ntopic,                                   
                 title=form.cleaned_data['title'],
                 status=0,
                 incite=c)
    arg.save()

    params = {'comment': form.cleaned_data['argument'],
              'user': request.user,
              'ntopic': c.ntopic,
              'debate': arg}

    opener = ArgComment(**params)
    opener.save()
    arg.save()

    msg_txt = ''.join([request.user.username, 
                       " has challenged you to a debate.\n\n[Click here](/argue/",
                       str(arg.id), "/) to view the debate and accept or decline",
                       "\n\nIf accepted, the debate will be active for 7 days, ",
                       "after which the participant with the most votes will win."])
    msg = tcdMessage(user=request.user,
                     recipient=defendant,
                     comment=msg_txt,
                     subject="Challenge!")
    msg.save()
    messages.info(request, "Challenged " + arg.defendant.username + " to a debate")
    return HttpResponseRedirect(redirect)

def vote(request):
    """Cast a vote for either the plaintiff or defendant in a debate"""
    if not request.POST:
        return render_to_AJAX(status="alert", messages=["Not a POST"])
    
    form = Ballot(request.POST)

    if not form.is_valid():
        return render_to_AJAX(status="alert", messages=["Invalid Form"])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['argument'])
    voter = get_object_or_404(User, pk=form.cleaned_data['voter'])
    redirect = ''.join(['/argue/', str(arg.id)])

    if not voter == request.user:
        return render_to_AJAX(status="alert", messages=["Can't cast vote as another user"])


    vote = nVote(argument=arg,
                 voter=voter,
                 voted_for=form.cleaned_data['voted_for'])
    vote.save()
    arg.calculate_score()
    arg.save()
    all_votes = nVote.objects.filter(argument=arg)
    
    return render_to_AJAX(status="ok", messages=[])

def unvote(request):

    if not request.POST:
        return render_to_AJAX(status="alert", messages=["Not a POST"])

    form = Ballot(request.POST)
    if not form.is_valid():
        return render_to_AJAX(status="alert", messages=["Invalid Form"])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['argument'])
    voter = get_object_or_404(User, pk=form.cleaned_data['voter'])
    redirect = ''.join(['/argue/', str(arg.id)])
    if not voter == request.user:
        return render_to_AJAX(status="alert", messages=["Can't delete another user's vote"])


    vote = get_object_or_404(nVote, argument=arg, voter=voter)
    vote.delete()
    arg.calculate_score()
    return render_to_AJAX(status="ok", messages=[])

def rebut(request):
    """Add a new post to an argument."""
    t = loader.get_template('items/msg_div.html')
    ct = Context({'id': "1",
                 'nesting': "20"})
                 
    if not request.POST:
        ct['message'] = "Not a POST"
        message = t.render(ct)
        return render_to_AJAX(status="error", messages=[message])

    form = RebutForm(request.POST)

    if not form.is_valid():
        ct['message'] = "Invalid Form"
        message = t.render(ct)
        return render_to_AJAX(status="error", messages=[message])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['arg_id'])

    if not arg.whos_up() == request.user:
        ct['message'] = "Not your turn"
        message = t.render(ct)
        return render_to_AJAX(status="error", messages=[message])

    if arg.status == 2:
        arg.status = 1
    elif arg.status == 1:
        arg.status = 2
    elif arg.status == 0:
        arg.status = 1
    params = {'comment': form.cleaned_data['comment'],
              'user': request.user,
              'ntopic': arg.topic,
              'debate': arg}

    c = ArgComment(**params)
    c.save()

    arg.save()

    top = arg.topic
    top.comment_length += len(c.comment)
    top.recalculate()
    top.save()

    t = loader.get_template('comments/arg_comment.html')
    context = Context({'comment': c,
                       'object': arg})
    return render_to_AJAX(status="ok", 
                          messages=[t.render(context),
                                    arg.get_status()])

def respond(request):
    """Potential opponent accepts or rejects a challenge to an argument."""    

    msg_t = loader.get_template("items/msg_div.html")
    ct = Context({'id': '1',
                 'nesting': '20'})
    
    if not request.POST:
        ct['message'] = "Not a POST"
        return render_to_AJAX(status='error', 
                              messages=[msg_t.render(ct)])


    form = Response(request.POST)

    if not form.is_valid():
        ct['message'] = "Invalid Form"
        return render_to_AJAX(status='error', 
                              messages=[msg_t.render(ct)])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['arg_id'])

    if not request.user == arg.defendant:
        ct['message'] = "Can't respond to a challenge that's not for you!"
        return render_to_AJAX(status='error', 
                              messages=[msg_t.render(ct)])

    redirect = '/argue/' + str(arg.id) + '/'
    
    if not arg.status == 0:
        ct['message'] = "Challenge already accepted or declined"
        return render_to_AJAX(status='error', 
                              messages=[msg_t.render(ct)])

    response = form.cleaned_data['response']
    if response == 0:
        # challenge accepted
        arg.status = 2
        arg.start_date = datetime.datetime.now()
        arg_response = "accept"
        message = ''.join([arg.defendant.username, 
                           " has accepted your challenge.\n\n[View this debate](", redirect, ")",
                           "\n\nThis debate will remain active for 7 days. After the time ",
                           "is up, the participant with the most votes will be declared the winner."])
        msg = tcdMessage(user=request.user,
                         recipient=arg.plaintiff,
                         comment=message,
                         subject="Challenge accepted",
                         pub_date=datetime.datetime.now())


    else:
        # response == 1, challenge declined
        # a value other than 0 or 1 would cause the form to not validate
        arg.status = 6
        arg.end_date = datetime.datetime.now()
        arg_response = "decline"                        
        message = ''.join([ arg.defendant.username, 
                            " has declined your challenge."])
        msg = tcdMessage(user=request.user,
                         recipient=arg.plaintiff,
                         comment=message,
                         subject="Challenge declined")

    msg.save()
    arg.save()
    status = "ok"
    ta_template = loader.get_template("items/turn_actions.html")
    ta_c = Context({'object': arg,
                    'user': request.user,
                    'last_c': arg.argcomment_set.order_by('-pub_date')[0]})
    turn_actions = ta_template.render(ta_c)
    response_message = msg.subject
    arg_status = arg.get_status()

    msg_t = loader.get_template("items/msg_div.html")
    msg_c = Context({'id': "1",
                     'message': response_message,
                     'nesting': "20"})

    return render_to_AJAX(status="ok", messages=[msg_t.render(msg_c),
                                                 turn_actions,
                                                 arg_response,
                                                 arg_status])

def draw(request):
    """A user offers that the debate be resolved as a draw."""
    status = "error"    
    t = loader.get_template('items/msg_div.html')
    ct = Context({'id': '1',
                  'nesting': '20'})

    if not request.POST:
        ct['message'] = "Not a POST"
        return render_to_AJAX(status="error", messages=[t.render(ct)])

    form = RebutForm(request.POST)
    if not form.is_valid():
        ct['message'] = "Invalid Form"
        return render_to_AJAX(status="error", messages=[t.render(ct)])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['arg_id'])
    redirect = ''.join(['/argue/', str(arg.id), '/'])
    if not arg.whos_up() == request.user:
        # Note this will also catch a draw offer to an argument that is inactive
        # because inactive arguments will return None to whos_up()
        # Also, it will catch offers from users who are not participants 
        # in the debate
        ct['message'] = "Not your turn"
        return render_to_AJAX(status="error", messages=[t.render(ct)])

    if arg.draw_set.all():
        ct['message'] = "A draw has already been offered"
        return render_to_AJAX(status="error", messages=[t.render(ct)])

    message = ''.join([request.user.username, 
                       " has offered a draw regarding the debate\n "
                       "[",  arg.title, "]", "(", redirect, ")",
                       "\nView the debate to accept or decline."])
    recipient = arg.get_opponent(request.user)
    msg = tcdMessage(user=request.user,
                     recipient=recipient,
                     comment=message,
                     subject="Draw?")

    msg.save()
    draw = Draw(offeror=request.user,
                recipient=arg.get_opponent(request.user),
                offer_date=datetime.datetime.now(),
                argument=arg)
    draw.save()
    return rebut(request)

def respond_draw(request):
    """Opponent responds to an offer of a draw"""
    
    msg_t = loader.get_template("items/msg_div.html")
    msg_c = Context({'id': "1",
                     'nesting': "20"})

    if not request.POST:
        msg_c['message'] = "Not a POST"
        return render_to_AJAX(status="error", messages=[msg_t.render(msg_c)])

    form = Response(request.POST)
    if not form.is_valid():
        msg_c['message'] = "Invalid Form"
        return render_to_AJAX(status="error", messages=[msg_t.render(msg_c)])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['arg_id'])
    draw = get_object_or_404(Draw, argument=arg)
    redirect = '/argue/' + str(arg.id) + '/'
    if not request.user == draw.recipient:
        msg_c['message'] = "You can't respond to this draw offer"
        return render_to_AJAX(status="error", messages=[msg_t.render(msg_c)])

    response = form.cleaned_data['response']
    if response == 0: # draw offer accepted
        message = ''.join([request.user.username, " has accepted your offer of a draw",
                           " regarding \n[", arg.title, "](", redirect, ")"])
        subject = "Draw Accepted"
        arg.status = 5            
    else: 
        # response == 1, the draw was declined 
        # if a value other than 0 or 1, the form would not have validated
        message = ''.join([request.user.username, " has declined your offer of a draw",
                           " regarding \n[", arg.title, "](", redirect, ")"])
        subject = "Draw Declined"

    msg = tcdMessage(user=request.user,
                     recipient = draw.offeror,
                     comment = message,
                     subject = subject)
    draw.delete()
    msg.save()
    arg.save()
    ta_template = loader.get_template("items/turn_actions.html")
    ta_c = Context({'object': arg,
                    'user': request.user,
                    'last_c': arg.argcomment_set.order_by('-pub_date')[0]})
    
    msg_c['message'] = msg.subject
    return render_to_AJAX(status="ok", messages=[msg_t.render(msg_c),
                                                 ta_template.render(ta_c), 
                                                 arg.get_status()])

def concede(request):
    """User concedes a debate, opponent wins"""
    status = "error"
    arg_status = None
    msg_t = loader.get_template('items/msg_div.html')
    msg_c = Context({'id': "1",
                 'nesting': "20"})
    
    if not request.POST:
        msg_c['message'] = "Not a POST"
        return render_to_AJAX(status="error", 
                              messages=[msg_t.render(msg_c)])

    form = Concession(request.POST)
    if not form.is_valid():
        msg_c['message'] = "Invalid Form"
        return render_to_AJAX(status="error", 
                              messages=[msg_t.render(msg_c)])

    arg = get_object_or_404(Debate, pk=form.cleaned_data['arg_id'])
    user = User.objects.get(pk=form.cleaned_data['user_id'])

    if not request.user == arg.whos_up():
        msg_c['message'] = "Not your turn"
        return render_to_AJAX(status="error", 
                              messages=[msg_t.render(msg_c)])

    arg.status += 2
    arg.end_date = datetime.datetime.now()
    recipient = arg.get_opponent(request.user)
    prof = Profile.objects.get(user = recipient)
    prof.score += 1
    message = ''.join([request.user.username, " has conceded in the debate\n", 
                       "[", arg.title, "]", "(/argue/", str(arg.id), "/)"])
    msg = tcdMessage(user=request.user,
                     recipient = recipient,
                     comment = message,
                     subject = "All right, you win")
    
    msg.save()
    arg.save()
    prof.save()
    msg_c['message'] = "Point conceded"

    return render_to_AJAX(status="ok",
                          messages=[msg_t.render(msg_c),
                                    arg.get_status()])

def arg_detail(request, object_id):
    arg = get_object_or_404(Debate, pk=object_id)
    voted_for = ''
    votes = nVote.objects.filter(argument=arg)
    arg_actions = ''
    last_c = arg.argcomment_set.order_by("-pub_date")[0]

    if request.user.is_authenticated():
        # find who the user voted for, if they voted
        try: 
            vote = votes.get(voter=request.user)
            if vote.voted_for == "P":
                voted_for = arg.plaintiff
            elif vote.voted_for == "D":
                voted_for = arg.defendant
            else:                
                messages.info(request, "Something funky about your vote")
        except nVote.DoesNotExist:
            pass        

    if arg.status in range(0,3):
        if request.user.is_authenticated():
            if request.user == arg.whos_up():
                if arg.status == 0:
                    # The challenge has been proposed but not accepted
                    argt=loader.get_template("items/arg_new_respond.html")
                    argc = Context({'object': arg,
                                    'request': request})
                    arg_actions = argt.render(argc)
                elif arg.draw_set.all():
                    # A draw has been offered
                    argt=loader.get_template("items/draw_actions.html")
                    argc = Context({'object': arg,
                                    'request': request})
                    arg_actions = argt.render(argc)
                else:
                    # normal turn
                    argt=loader.get_template("items/turn_actions.html")
                    argc = Context({'object': arg,
                                    'last_c': last_c,
                                    'user': request.user})
                    arg_actions = argt.render(argc)
            elif request.user == arg.whos_up(invert=1):
                # The user is a participant, but it's not his turn
                arg_actions = ''
            else:
                # The user is not a participant in this debate
                if voted_for:
                    # The user has already cast a vote
                    argt = loader.get_template("items/vote_tally.html")
                    argc = Context({'pvotes': votes.filter(voted_for='P').count(),
                                    'dvotes': votes.filter(voted_for='D').count(),
                                    'object': arg,
                                    'current': True,
                                    'voted_for': voted_for,
                                    'request': request
                                    })
                    arg_actions = argt.render(argc)    
                else:
                    # The user hasn't cast a vote yet
                    argt = loader.get_template("items/vote_div.html")
                    argc = Context({'object': arg,
                                    'request': request})
                    arg_actions = argt.render(argc)
        else:
            # debate is in progress, tell user to log in to vote
            argt = loader.get_template("items/arg_login.html")
            argc = Context({'request': request})
            arg_actions = argt.render(argc)    
    else: 
        # debate has ended, show the final vote tally
        argt = loader.get_template("items/vote_tally.html")
        argc = Context({'pvotes': votes.filter(voted_for='P').count(),
                        'dvotes': votes.filter(voted_for='D').count(),
                        'object': arg,
                        'current': False,
                        'voted_for': voted_for
                        })
        arg_actions = argt.render(argc)    

    return render_to_response("items/arg_detail.html",
                              {'object': arg,
                               'incite': arg.incite,
                               'comments': arg.argcomment_set.order_by('pub_date'),
                               'last_c': last_c,
                               'arg_actions': arg_actions
                               },
                              context_instance=RequestContext(request))

def args_list(request, sort, page=1):

    if sort == "new":
        args = Debate.objects.filter(status__range=(1,2)).order_by('-start_date')
        template_name = "items/arg_new.html"
    elif sort == "hot":
        args = Debate.objects.filter(status__range=(1,2))
        template_name = "items/arg_current.html"
    elif sort == "archive":
        args = Debate.objects.filter(status__range=(3,5)).order_by('-start_date')
        template_name = "items/arg_old.html"
        
    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False

    paginate_by = 25
    extra_context = {'start': calc_start(page, paginate_by, args.count()),
                     'newwin': newwin}

    return list_detail.object_list(request=request, queryset=args, paginate_by=paginate_by,page=page,
                                   template_object_name = 'args',
                                   template_name = template_name,
                                   extra_context=extra_context)

def review(request, model, page=1):
    if not (request.user.is_authenticated() and request.user.is_staff):
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

    paginate_by=50

    item=models[model]

    queryset = item.objects.filter(needs_review=True,
                                  spam=False)
    prof = get_object_or_404(Profile, user=request.user)
    return list_detail.object_list(request=request, queryset=queryset,
                                   paginate_by=paginate_by, page=page,
                                   template_object_name = model,
                                   template_name="items/review_" + model +".html",
                                   extra_context={'newwin': prof.newwin,
                                                  'start': calc_start(page, paginate_by, queryset.count())})

def decide(request, model):
    if not (request.user.is_authenticated() and request.user.is_staff):
        return render_to_AJAX(status="alert", messages=["Unauthorized"])
    
    if not request.POST:
        return render_to_AJAX(status="alert", messages=["Not a POST"])
    
    form = DecideForm(request.POST)
    if not form.is_valid():
        return render_to_AJAX(status="alert", messages=["Invalid Form"])
    
    item = models[model]
    try:
        obj = item.objects.get(id=form.cleaned_data['id'], needs_review=True)
    except item.DoesNotExist:
        return render_to_AJAX(status="alert", messages=["Object not found"])

    if form.cleaned_data['decision'] == 0:
        # Approved
        obj.needs_review = False
        if model == "comment":
            obj.pub_date = datetime.datetime.now()
            # Alert followers that a reply has been made
            top = obj.ntopic
            if obj.nparent_id == 0:
                followers = top.followers.all()
            else:
                parent = TopicComment.objects.get(id=obj.nparent_id)
                followers = parent.followers.all()

            for follower in followers:
                msg = fcomMessage(recipient=follower,
                                  is_read=False,
                                  reply=obj,
                                  pub_date=datetime.datetime.now())
                msg.save()
        elif model == "topic":
            obj.sub_date = datetime.datetime.now()
            
        obj.save()
        message = render_message(model + " approved", 10)

    elif form.cleaned_data['decision'] == 1:
        # Mark spam, disable user
        obj.spam = True
        obj.score = 0
        obj.save()
        prof = Profile.objects.get(user=obj.user)
        prof.rate = 10
        prof.save()
        message = render_message(model + " marked as spam. User disabled.", 10)
    else:
        # Rejected, marked spam but user not disabled
        # 'decision' == 2, other values will cause an invalid form
        obj.spam = True
        obj.score = 0
        obj.save()
        message = render_message(model + " rejected.", 10)

    return render_to_AJAX(status="ok", messages=[message])
        
    
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

    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False

    # calculate the number of the first object on this page
    # in case the objects are paginated and want to be displayed as 
    # a numbered list
    extra_context = {'start': calc_start(page, paginate_by, obj_list.count()),
                     'newwin': newwin,
                     foreign_field: foreign_obj}



    return list_detail.object_list(request=request, queryset=obj_list, 
                                   extra_context=extra_context,
                                   paginate_by=paginate_by, page=page, 
                                   allow_empty=allow_empty, template_name=template_name,
                                   template_loader=template_loader, 
                                   context_processors=context_processors,
                                   template_object_name=template_object_name,
                                   mimetype=mimetype)




