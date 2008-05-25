from django.contrib.auth.models import User
from django.contrib import auth
from django import oldforms as forms
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import list_detail

from tcd.items.models import Topic
from tcd.items.forms import tcdUserCreationForm, tcdLoginForm
from tcd.comments.models import Comment
from tcd.comments.forms import CommentForm

import datetime

def comments(request, topic_id):
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.comment_set
    first_c = comments.filter(is_first=True)
    rest_c = comments.filter(is_first=False)
    form_comment = CommentForm()
    if request.user.is_authenticated():
        logged_in = True
        user = request.user.username
    else:
        logged_in = False
        user = None
    return render_to_response('items/topic_detail.html', {'object': top,
                                                          'first_c': first_c,
                                                          'rest_c': rest_c,
                                                          'logged_in': logged_in,
                                                          'user': user,
                                                          'next': request.path,
                                                          'form_comment': form_comment
                                                          })

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
            return HttpResponseRedirect("/login?next=" + request.POST['next'])
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
            user = User.objects.get(email=email)
            user = auth.authenticate(username=user.username, password=data['password'])
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next)                
            else:
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

def topics(request):
    if request.user.is_authenticated():
        logged_in = True
        user = request.user.username
    else:
        logged_in = False
        user = None
    return list_detail.object_list(
        request,
        queryset=Topic.objects.all(),
        template_name= "items/topic_list.html",
        template_object_name = "object",
        extra_context = {"logged_in": logged_in,
                         "user": user,
                         "next": "/"})
