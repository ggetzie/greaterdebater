from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.views.generic import list_detail

from tcd.comments.models import Comment, tcdMessage
from tcd.items.models import Topic, Argument
from tcd.items.views import object_list_field, object_list_foreign_field, calc_start
from tcd.profiles.forms import tcdUserCreationForm, tcdPasswordResetForm, tcdLoginForm, forgotForm, FeedbackForm
from tcd.profiles.models import Profile, Forgotten
from tcd.utils import random_string

import datetime
import MySQLdb
import pyfo

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
                try:
                    # check whether an active request for this user to reset his password exists
                    temp = Forgotten.objects.get(user=user)
                    message = """A forgotten password request has been submitted for this
account. Please check your email and follow the link provided to reset your password"""
                except ObjectDoesNotExist:
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
    paginate_by = 10
    user = get_object_or_404(User, username=value)
    args = user.defendant_set.all() | user.plaintiff_set.all()
    return list_detail.object_list(request=request,
                                   queryset=args,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name="registration/profile/profile_args.html",
                                   template_object_name='args',
                                   extra_context={'username': user,
                                                  'start': calc_start(page, paginate_by, args.count())})

def profile_msgs(request, value, page=1):
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
                'template_object_name': 'messages',
                'paginate_by': 25,
                'page': page
                }
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

def reset_password(request, value, code=None):
    """ Reset a user's password """
    user = get_object_or_404(User, username=value)
    redirect_to = ''.join(['/users/u/', user.username, '/settings/'])
    temp = None    
    if request.POST:
            data = request.POST.copy()
            form = tcdPasswordResetForm(data)
            if form.is_valid():
                code = form.cleaned_data.get('code', '')
                if code and len(code) == 32:
                    temp = get_object_or_404(Forgotten, code=code)
                if user == request.user or temp:
                    user.set_password(form.cleaned_data['new_password1'])
                    user.save()
                    user.message_set.create(message="Password Changed!")                    
                    if temp:
                        user = auth.authenticate(username=user.username, password=form.cleaned_data['new_password1'])
                        if user is not None and user.is_active:
                            auth.login(request, user)
                        temp.delete()
                    return HttpResponseRedirect(redirect_to)
    else:
        if code and len(code) == 32:
            temp = get_object_or_404(Forgotten, code=code)
        if user == request.user or temp:
            form = tcdPasswordResetForm()
        else:
            return HttpResponseForbidden("<h1>Unauthorized</h1>")
    return render_to_response("registration/profile/reset.html",
                              {'form': form,
                               'username': user,
                               'code': code},
                              context_instance=RequestContext(request))

def feedback(request):        
    if request.POST:
        form = FeedbackForm(request.POST)
        if form.is_valid():            
            if request.user.is_authenticated():
                message = '\n\n'.join([form.cleaned_data['message'], 
                                       '\n'.join([''.join(["username: ", request.user.username]), 
                                                  ''.join(["email: ", request.user.email])])])
            else:
                message = '\n\n'.join([form.cleaned_data['message'], "Anonymous user"])
            send_mail(form.cleaned_data['subject'],
                      message,
                      'admin@kotsf.com',
                      ['ggetzie@gmail.com'],
                      fail_silently=False)            
            return HttpResponseRedirect("/users/thanks")
    else:
        form = FeedbackForm()
        feedback_context = {'form': form}
             
    return render_to_response("registration/feedback.html",
                              feedback_context,
                              context_instance=RequestContext(request))

def forgot_password(request):
    if request.POST:
        data = request.POST.copy()
        form = forgotForm(data)
        if form.is_valid():
            # store the user and a randomly generated code in the database
            user = User.objects.get(email=form.cleaned_data['email'])
            code = save_forgotten(user)
            message = ''.join(["To reset your password, visit the address below:\nhttp://kotsf.com/users/u/",
                               user.username, "/reset/", code])
            send_mail('Reset your password at kotsf.com', message, 'admin@kotsf.com', [user.email], 
                      fail_silently=False)
            return render_to_response("registration/profile/forgot.html",
                                      {'form': form,
                                       'message': "An email with instructions for resetting your password has been sent to the address you provided."},
                                      context_instance=RequestContext(request))

    else:
        form = forgotForm()
    return render_to_response("registration/profile/forgot.html",
                              {'form': form},
                              context_instance=RequestContext(request))

def delete_messages(request):
    if request.POST:
        message_list = request.POST['message_list']
        message_list = [int(i) for i in message_list.split(',')]
        messages = tcdMessage.objects.filter(pk__in=message_list)
        messages.delete()
        sys_message="Messages Deleted"
    else:
        sys_message = "Not a POST"
    response = ('response', [('message', sys_message)])
    response = pyfo.pyfo(response, prolog=True, pretty=True, encoding='utf-8')
    return HttpResponse(response)



def save_forgotten(user):
    """When saving a temporary entry to the forgotten password table, there is a 
_very_ small chance that we will randomly generate a code that is already in the
table. To deal with that we catch an integrity error from the database, and try to 
resubmit with a new randomly generated code."""
    try:
        code = random_string(32)
        temp = Forgotten(user=user, code=code)
        temp.save()
        # return the randomly generated code so it can be sent in an email
        # to the user
        return code
    except MySQLdb.IntegrityError:
        save_forgotten(user)

