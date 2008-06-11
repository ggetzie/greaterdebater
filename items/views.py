from django import oldforms as forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail

from tcd.items.models import Topic, Argument, Profile
from tcd.items.forms import *
from tcd.comments.models import Comment
from tcd.comments.forms import CommentForm

import datetime

image_url="http://localhost/static/s.gif"

def build_list(comments, p_id):
    """Takes a query set of comments and a parent id and
    returns a list of comments sorted in the appropriate parent-child
    order such that first comment = first toplevel comment, second commend = first
    child of first comment, third comment = first child of second comment or second 
    child of first comment and so on"""
    comment_list = []
    for comment in comments.filter(parent_id=p_id):
        children = comments.filter(parent_id=comment.id)
        if not children:
            comment_list.append(comment)
        else:
            comment_list.append(comment)
            comment_list.extend(build_list(comments, comment.id))
    return comment_list

def comments(request, topic_id):
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.comment_set
    first_c = comments.filter(is_first=True)
    rest_c = build_list(comments.filter(is_first=False), 0)
    form_comment = CommentForm()
    if request.user.is_authenticated():
        user = request.user.username
    else:
        logged_in = False
        user = None
    return render_to_response('items/topic_detail.html', 
                              {'object': top,
                               'first_c': first_c,
                               'rest_c': rest_c,
                               'next': request.path,
                               'form_comment': form_comment,
                               'image_url': image_url},
                              context_instance=RequestContext(request)
                              )

def register(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = tcdUserCreationForm(data)
        next = request.POST['next']
        if form.is_valid():
            new_user = User.objects.create_user(username=data['username'],
                                                password=data['password1'],
                                                email=data['email'])
            new_user.is_staff=False
            new_user.is_superuser=False
            new_user.is_active=True
            new_user.save()
            new_user = auth.authenticate(username=new_user.username,
                                         password=data['password1'])
            auth.login(request, new_user)
            new_user_profile = Profile(user=new_user,
                                       score=1)
            new_user_profile.save()
            return HttpResponseRedirect(next)
    else:
        form = tcdUserCreationForm()
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = "/"    
    return render_to_response("registration/register.html", 
                              {'form' : form,
                               'next' : next})

def login(request):
    message = None
    if request.method == 'POST':
        data = request.POST.copy()
        form = tcdLoginForm(data)
        next = request.POST['next']
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                user = auth.authenticate(username=user.username, password=data['password'])
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(next)                
                else:
                    form = tcdLoginForm()
                    message = "Sorry, that's not a valid username or password"
            except ObjectDoesNotExist:
                form = tcdLoginForm()
                message = "Sorry, that's not a valid username or password"
    else:
        form = tcdLoginForm()
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = "/"
    return render_to_response("registration/login.html",
                              {'form': form,
                               'next': next,
                               'message': message})

def submit(request):
    if request.user.is_authenticated():
        user = request.user.username
        if request.method == 'POST':
            data = request.POST.copy()
            form = tcdTopicSubmitForm(data)
            if form.is_valid():
                topic = Topic(user=request.user,
                              title=form.cleaned_data['title'],
                              score=1,
                              sub_date=datetime.datetime.now())
                topic.save()
                next = "/" + str(topic.id) + "/"
                if data['url']:
                    topic.url = form.cleaned_data['url']
                else:
                    topic.url = next
                topic.save()
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
            form = tcdTopicSubmitForm()
            return render_to_response("items/submit.html",
                                      {'form': form},
                                      context_instance=RequestContext(request))

    else:
        return render_to_response("registration/login.html",
                                  {'next': '/submit/',
                                   'message': "Please log in to submit a topic",
                                   'form': tcdLoginForm()},
                                  context_instance=RequestContext(request))

                                  
def topics(request):
    return render_to_response("items/topic_list.html",
                              {'object_list': Topic.objects.all()[:25]},
                              context_instance=RequestContext(request))

def challenge(request, df_id, c_id):
    defendant = get_object_or_404(User, username=df_id)
    c = get_object_or_404(Comment, pk=c_id)
    if Argument.objects.filter(plaintiff=request.user,
                               comment=c_id):
        request.user.message_set.create(message="Already started this argument")
    else:
        arg = Argument(plaintiff=request.user,
                       defendant=defendant,
                       start_date=datetime.datetime.now(),
                       topic=c.topic,
                       title= ''.join([c.comment[:20], '...']),
                       status=0)
        arg.save()
        c.arguments.add(arg)
        c.save()
        request.user.message_set.create(message= ''.join(["Challenged ", arg.defendant.username, " to an argument"]))
    return HttpResponseRedirect(''.join(['/', str(c.topic_id), '/']))

def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_info = get_object_or_404(Profile, user=user)
    return render_to_response("registration/profile/profile_home.html",
                              {'user_id': user,
                               'user_info': user_info},
                              context_instance=RequestContext(request))

def profile_args(request, username):
    user = get_object_or_404(User, username=username)
    args = user.defendant_set.all() | user.plaintiff_set.all()
    return render_to_response("registration/profile/profile_args.html",
                              {'user_id': user,
                               'args': args.order_by('start_date')},
                              context_instance=RequestContext(request))

