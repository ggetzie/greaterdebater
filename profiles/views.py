from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.views.generic import list_detail

from tcd.comments.models import Comment, tcdMessage
from tcd.items.forms import tcdUserCreationForm, tcdPasswordResetForm, tcdLoginForm
from tcd.items.models import Topic, Argument
from tcd.items.views import object_list_field, object_list_foreign_field
from tcd.profiles.models import Profile
from tcd.utils import random_string

import datetime

def register(request):
    """Create an account for a new user"""
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
                               'redirect' : next})

def login(request):
    """Log in a user"""
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
                    # redirect the user to the page they were looking at
                    # before they tried to log in
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
                               'redirect': next,
                               'message': message})
def profile(request, value):
    """Display a users profile"""
    
    # The user whose profile we wish to display (not necessarily the user viewing it)
    user = get_object_or_404(User, username=value)
    user_info = get_object_or_404(Profile, user=user)
    return render_to_response("registration/profile/profile_home.html",
                              {'username': user,
                               'user_info': user_info,},
                              context_instance=RequestContext(request))

def profile_args(request, value, page=1):
    """Display a list of all arguments a user has been involved in."""
    
    user = get_object_or_404(User, username=value)
    args = user.defendant_set.all() | user.plaintiff_set.all()
    return list_detail.object_list(request=request,
                                   queryset=args,
                                   paginate_by=3,
                                   page=page,
                                   template_name="registration/profile/profile_args.html",
                                   template_object_name='args',
                                   extra_context={'username': user})

def profile_msgs(request, value):
    """ Display a list of all the user's messages. Only display if the user
    trying to view them is the user they belong to."""
    
    user = get_object_or_404(User, username=value)
    if request.user == user:
        args = {'request': request,
                'value': value,
                'model': tcdMessage,
                'field': 'recipient',
                'fv_dict': {'is_msg': True},
                'foreign_model': User,
                'foreign_field': 'username',
                'template_name': "registration/profile/profile_msgs.html",
                'template_object_name': 'messages'}
        return object_list_foreign_field(**args)
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def message_detail(request, value, object_id):
    message = tcdMessage.objects.get(comment_ptr=object_id)
    user = User.objects.get(username=value)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render_to_response("registration/profile/message_detail.html",
                              {'comment': message,
                               'username': user},
                              context_instance=RequestContext(request))

def profile_stgs(request, value):
    """ Display the users current settings and allow them to be modified """
    
    user = get_object_or_404(User, username=value)
    if request.user == user:
        return render_to_response("registration/profile/settings.html",
                                  {'username': user},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def reset_password(request, value):
    """ Reset a user's password """
    user = get_object_or_404(User, username=value)
    redirect_to = ''.join(['/', user.username, '/settings/'])
    if user == request.user:
        if request.POST:
            data = request.POST.copy()
            form = tcdPasswordResetForm(data)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                user.message_set.create(message="Password Changed!")
                return HttpResponseRedirect(redirect_to)
        else:
            form = tcdPasswordResetForm()
        return render_to_response("registration/profile/reset.html",
                                  {'form': form,
                                   'username': user},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")
