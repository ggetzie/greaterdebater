from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext, Context
from django.views.generic import list_detail

from tcd.comments.models import TopicComment, ArgComment, Debate, tcdMessage, \
    fcomMessage

from tcd.items.models import Topic, Tags
from tcd.items.views import object_list_field, object_list_foreign_field, calc_start

from tcd.profiles.forms import tcdUserCreationForm, tcdPasswordResetForm, tcdLoginForm, \
    forgotForm, FeedbackForm, SettingsForm
from tcd.profiles.models import Profile, Forgotten

from tcd.settings import HOSTNAME
from tcd.utils import random_string, tag_dict, tag_string, render_to_AJAX, render_message

import datetime
import MySQLdb
import pyfo
import urllib

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
                                       score=0
                                       )
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
                               'redirect' : next},
                              context_instance=RequestContext(request)
                              )

def login(request):
    """Log in a user"""
    message = None
    form = tcdLoginForm()
    rform = tcdUserCreationForm()
    if request.method == 'POST':
        data = request.POST.copy()
        form = tcdLoginForm(data)
        if 'next' in request.POST:
            next = request.POST['next']
        else:
            next = '/'
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
                        message = "Sorry, that's not a valid username or password"
            except ObjectDoesNotExist:
                message = "Sorry, that's not a valid username or password"
    else:
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = "/"
    return render_to_response("registration/login.html",
                              {'form': form,
                               'rform': rform,
                               'redirect': next,
                               'message': message},
                              context_instance=RequestContext(request))
def profile(request, value):
    """Display a users profile"""
    
    # The user whose profile we wish to display (not necessarily the user viewing it)
    user = get_object_or_404(User, username=value)
    user_info = get_object_or_404(Profile, user=user)
    return render_to_response("registration/profile/profile_home.html",
                              {'username': user,
                               'user_info': user_info,},
                              context_instance=RequestContext(request))

def profile_topics(request, value, page=1):
    paginate_by = 25
    user = get_object_or_404(User, username=value)
    topics = Topic.objects.filter(user=user).order_by('-sub_date')

    if request.user.is_authenticated():        
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False

    return list_detail.object_list(request=request,
                                   queryset=topics,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name="registration/profile/profile_tops.html",
                                   template_object_name='topics',
                                   extra_context={'username': user,
                                                  'start': calc_start(page, paginate_by, topics.count()),
                                                  'newwin': newwin})

def profile_saved(request, value, tag=None, page=1):
    paginate_by = 25
    user = get_object_or_404(User, username=value)

    if user == request.user:
        prof = get_object_or_404(Profile, user=request.user)
        user_tags = Tags.objects.filter(user=user)
        if tag:
            # escape regex meta characters allowed in tags
            safetag = tag.replace("?", "\?")
            safetag = safetag.replace("$", "\$")
            safetag = safetag.replace("'", "\'")
            
            user_tags = user_tags.filter(tags__regex="(^|,)" + safetag + "(,|$)")

        utags = tag_dict(prof.tags)
        utl = utags.keys()
        utl.sort()
        return list_detail.object_list(request=request,
                                       queryset=user_tags.order_by('-topic__sub_date'),
                                       paginate_by=paginate_by,
                                       page=page,
                                       template_name="registration/profile/profile_savd.html",
                                       template_object_name='user_tags',
                                       extra_context={'username': user,
                                                      'start': calc_start(page, paginate_by, user_tags.count()),
                                                      'newwin': prof.newwin,
                                                      'utags': utl,
                                                      'filter_tag': tag,
                                                      'source': 1
                                                      })
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def tagedit(request, value, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    user = get_object_or_404(User, username=value)
    tags = get_object_or_404(Tags, topic=topic, user=user)
    tag_list = tags.tags.split(',')
    if not user == request.user:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")
    return render_to_response("registration/profile/tagedit.html",
                              {'topic':topic,
                               'tag_list':tag_list,
                               'username':user},
                              context_instance=RequestContext(request))


def profile_args(request, value):
    """Display a list of all arguments a user has been involved in."""

    user = get_object_or_404(User, username=value)
    args = user.defendant_set.all() | user.plaintiff_set.all()
    pending = args.filter(status=0).order_by('-start_date')    
    current = args.filter(status__range=(1,2)).order_by('-start_date')
    complete = args.filter(status__range=(3,6)).order_by('-start_date')
    
    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False

    return render_to_response("registration/profile/profile_args.html",
                              {'username': user,
                               'pending': pending[:5],
                               'more_pending': len(pending) > 5,
                               'current': current[:5],
                               'more_current': len(current) > 5,
                               'complete': complete[:5],
                               'more_complete': len(complete) > 5,
                               'newwin': newwin
                               },
                              context_instance=RequestContext(request))

def profile_all_args(request, value, aset, page=1):

    paginate_by = 10

    user = get_object_or_404(User, username=value)
    
    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False
    
    if aset == "pending":
        status = (0,0)
        title = "Pending"
    elif aset == "current":
        status = (1,2)
        title = "Active"
    elif aset == "complete":
        status = (3,6)
        title = "Completed"
        

    args = user.defendant_set.filter(status__range=status) |  user.plaintiff_set.filter(status__range=status)

    return list_detail.object_list(request=request,
                                   queryset=args.order_by('-start_date'),
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name="registration/profile/all_args.html",
                                   template_object_name='args',
                                   extra_context={'username': user,
                                                  'start': calc_start(page, paginate_by, args.count()),
                                                  'aset': aset,
                                                  'newwin': newwin,
                                                  'title': title})

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
                'page': page,
                'extra_context': {'username': user}
                }
        return object_list_foreign_field(**args)
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def message_detail(request, value, object_id):
    user = get_object_or_404(User, username=value)
    if user != request.user: return HttpResponseForbidden("<h1>Unauthorized</h1>")

    message_list = tcdMessage.objects.filter(recipient=user).order_by('-pub_date')    
    message = message_list.get(comment_ptr=object_id)
    try:
        next = message_list.filter(pub_date__gt=message.pub_date).order_by('pub_date')[0].id
    except IndexError:
        next = ""
    try:
        prev = message_list.filter(pub_date__lt=message.pub_date).order_by('-pub_date')[0].id
    except IndexError:
        prev = ""
    if not message.is_read:
        message.is_read = True
        message.save()
    return render_to_response("registration/profile/message_detail.html",
                              {'comment': message,
                               'username': user,
                               'next': str(next),
                               'prev': str(prev)},
                              context_instance=RequestContext(request))

def replies(request, value, page=1):
    user = get_object_or_404(User, username=value)
    if user != request.user: return HttpResponseForbidden("<h1>Unauthorized</h1>")
    new_replies = fcomMessage.objects.filter(recipient=user)
    return list_detail.object_list(request=request,
                                   queryset=new_replies,
                                   page=page,
                                   paginate_by=25,
                                   template_name="registration/profile/replies.html",
                                   template_object_name="replies",
                                   extra_context={'username': user})

def mark_read(request):
    status="error"
    if not request.POST: return render_to_AJAX(status=status,
                                               messages=[render_message("Not a POST", 10)])
    try:
        msg = fcomMessage.objects.get(pk=request.POST['id'])
        if not request.user == msg.recipient:
            return render_to_AJAX(status=status,
                                  messages=[render_message("Not for you", 10)])
        msg.is_read = True
        msg.save()
        count = len(fcomMessage.objects.filter(recipient=request.user, is_read=False))
        messages = [render_message("marked as read", 10), count]
        status = "ok"
    except ObjectDoesNotExist:
        messages = ["Message does not exist"]

    return render_to_AJAX(status=status,
                          messages=messages)
                                   
def check_messages(request):
    status = "error"
    num = 0
    if not request.user.is_authenticated():
            return render_to_AJAX(status=status,
                                  messages=["Not Logged In"])

    msgs = tcdMessage.objects.filter(recipient=request.user, is_read=False)
    cmsgs = fcomMessage.objects.filter(recipient=request.user, is_read=False)

    css = []
    for m in (msgs, cmsgs):
        if len(m) > 0:
            css.append("class=unread_msg")
        else:
            css.append('')

    msgt = loader.get_template('registration/profile/user_msgs.html')
    msgc = Context({'css': css,
                    'tcdnum': len(msgs),
                    'cfnum': len(cmsgs),
                    'username': request.user.username})
    message = msgt.render(msgc)
    status = "ok"

    return render_to_AJAX(status=status,
                          messages=[message])
                          

def profile_stgs(request, value):
    """ Display the users current settings and allow them to be modified """
    
    user = get_object_or_404(User, username=value)
    prof = get_object_or_404(Profile, user=user)

    if request.user != user: return HttpResponseForbidden("<h1>Unauthorized</h1>")

    if request.POST:
        form = SettingsForm(request.POST)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            prof.newwin = form.cleaned_data['newwindows']
            prof.feedcoms = form.cleaned_data['feedcoms']
            prof.feedtops = form.cleaned_data['feedtops']
            prof.feeddebs = form.cleaned_data['feeddebs']
            prof.followcoms = form.cleaned_data['followcoms']
            prof.followtops = form.cleaned_data['followtops']
            user.save()
            prof.save()
            messages.info(request, "Changes saved")
    else:
        form = SettingsForm({'newwindows': prof.newwin,
                             'feedcoms': prof.feedcoms,
                             'feedtops': prof.feedtops,
                             'feeddebs': prof.feeddebs,
                             'request_email': user.email,
                             'email': user.email,
                             'followcoms': prof.followcoms,
                             'followtops': prof.followtops
                             })


    return render_to_response("registration/profile/settings.html",
                              {'username': user,
                               'form': form,
                               'prof': prof},
                              context_instance=RequestContext(request))

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
                if code:
                    temp = get_object_or_404(Forgotten, code=code)
                if not (temp or user == request.user):
                    return HttpResponseForbidden("<h1>Unauthorized</h1>")

                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.info(request, "Password changed!")
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
    form = FeedbackForm()
    if request.POST:
        form = FeedbackForm(request.POST)
        if form.is_valid():            
            if request.user.is_authenticated():
                message = '\n\n'.join([form.cleaned_data['message'], 
                                       '\n'.join([''.join(["username: ", request.user.username]), 
                                                  ''.join(["email: ", request.user.email])])])
            else:
                message = '\n\n'.join([form.cleaned_data['message'], "Anonymous user"])
            subj = form.cleaned_data['subject']

            send_mail(subj,
                      message,
                      'dnr@greaterdebater.com',
                      ['feedback@greaterdebater.com'],
                      fail_silently=False)            
            return HttpResponseRedirect("/users/thanks")
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
            
            # Delete any previous codes in the database for this user
            old_forgots = Forgotten.objects.filter(user=user)
            for f in old_forgots:
                f.delete()

            code = save_forgotten(user)
            message = ''.join(["To reset your password, visit the address below:\n",
                               HOSTNAME, "/users/u/",
                               user.username, "/reset/", code])
            send_mail('Reset your password at GreaterDebater', 
                      message, 
                      'dnr@greaterdebater.com', 
                      [user.email], 
                      fail_silently=False)
            messages.info(request, 
                          "An email with instructions for resetting your password has been sent to the address you provided.")
            return render_to_response("registration/profile/forgot.html",
                                      context_instance=RequestContext(request))

    else:
        form = forgotForm()
    return render_to_response("registration/profile/forgot.html",
                              {'form': form},
                              context_instance=RequestContext(request))

def delete_messages(request):
    if not request.POST:
        return render_to_AJAX(status="error", messages=["Not a POST"])
    
    try:
        message_list=request.POST['message_list']
    except KeyError:
        return render_to_AJAX(status="error", messages=["No message list"])

    message_list = [int(i) for i in message_list.split(',')]
    msgs = tcdMessage.objects.filter(pk__in=message_list)
    for m in msgs:
        if not request.user == m.recipient:
            return render_to_AJAX(status="error", messages=["Messages could not be deleted"])
    
    msgs.delete()
    return render_to_AJAX(status='ok', messages=["Messages deleted."])

def delete_current_message(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

    redirect = '/users/u/' + request.user.username + '/messages/'
    if not request.POST:
        messages.error(request, "Not a POST")
        return HttpResponseRedirect(redirect)

    try:
        m_id = int(request.POST['message_id'])
    except KeyError:
        messages.error(request, "No message id found")
        return HttpResponseRedirect(redirect)
                                    
    message_list = tcdMessage.objects.filter(recipient=request.user).order_by('pub_date')
    
    message = get_object_or_404(tcdMessage, pk=m_id)
    if not message.recipient == request.user:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

    try:
        redirect = ''.join(['/users/u/', request.user.username, 
                            '/messages/', 
                            str(message_list.filter(pub_date__gt=message.pub_date).order_by('pub_date')[0].id)])
    except IndexError:
        redirect = ''.join(['/users/u/', request.user.username, 
                            '/messages/'])

    message.delete()
    messages.info(request, "Message deleted")
    return HttpResponseRedirect(redirect)

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
