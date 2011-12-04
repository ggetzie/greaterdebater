from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.template import loader, RequestContext, Context
from django.views.generic.list import ListView

from comments.models import TopicComment, ArgComment, Debate, tcdMessage, \
    fcomMessage

from items.models import Topic, Tags

from profiles.forms import tcdUserCreationForm, tcdPasswordResetForm, tcdLoginForm, \
    forgotForm, FeedbackForm, SettingsForm
from profiles.models import Profile, Forgotten

from settings import HOSTNAME
from utils import random_string, tag_dict, tag_string, render_to_AJAX, render_message

import datetime
import MySQLdb
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
        next = request.POST.get('next', '/')
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
        next = request.GET.get('next', '/')
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

class ProfileTopicView(ListView):

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['value'])
        topics = Topic.objects.filter(user=self.user).order_by('-sub_date')
        return topics

    def get_context_data(self, **kwargs):
        context = super(ProfileTopicView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            prof = get_object_or_404(Profile, user=self.request.user)
            newwin = prof.newwin
        else:
            newwin = False
            
        page_root = '/users/u/' + self.user.username +'/submissions'
        context.update({'username': self.user,
                        'newwin': newwin,
                        'page_root': page_root})
        return context

class ProfileCommentView(ListView):
    
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['value'])
        comments = TopicComment.objects.filter(user=self.user).order_by('-pub_date')
        return comments

    def get_context_data(self, **kwargs):
        context = super(ProfileCommentView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            prof = get_object_or_404(Profile, user=self.request.user)
            newwin = prof.newwin
        else:
            newwin = False
            
        page_root = '/users/u/' + self.user.username +'/comments'
        context.update({'username': self.user,
                        'newwin': newwin,
                        'page_root': page_root})
        return context

class ProfileSavedView(ListView):

    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, *args, **kwargs):
        return super(ProfileSavedView, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        self.prof = get_object_or_404(Profile, user=self.request.user)
        self.user_tags = Tags.objects.filter(user=self.request.user)
        self.tag = self.kwargs.get('tag', None)
        if self.tag:
            # escape regex meta characters allowed in tags
            safetag = self.tag.replace("?", "\?")
            safetag = safetag.replace("$", "\$")
            safetag = safetag.replace("'", "\'")
            
            self.user_tags = self.user_tags.filter(tags__regex="(^|,)" + safetag + "(,|$)")



        return self.user_tags.order_by('-topic__sub_date')
        
    def get_context_data(self, **kwargs):
        context = super(ProfileSavedView, self).get_context_data(**kwargs)

        self.utags = tag_dict(self.prof.tags)
        self.utl = self.utags.keys()
        self.utl.sort()
        if self.tag:
            page_root = '/users/u/%s/saved/%s/page' % (self.request.user.username, self.tag)
        else:
            page_root = '/users/u/%s/saved/page' % self.request.user.username
        
        
        context.update({'newwin': self.prof.newwin,
                        'username': self.request.user,
                        'utags': self.utl,
                        'filter_tag': self.kwargs.get('tag', None),
                        'source': 1,
                        'page_root': page_root})
        return context


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

class ProfileAllArgs(ListView):
    
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['value'])
        self.aset_dict = {"pending":((0,0), "Pending"),
                          "current":((1,2), "Active"),
                          "complete":((3,6), "Completed")}

        self.status, self.title = self.aset_dict[self.kwargs['aset']]
        
        args = self.user.defendant_set.filter(status__range=self.status) | \
        self.user.plaintiff_set.filter(status__range=self.status)
        return args
    
    def get_context_data(self, **kwargs):
        context = super(ProfileAllArgs, self).get_context_data(**kwargs)
        
        if self.request.user.is_authenticated():
            prof = get_object_or_404(Profile, user=self.request.user)
            newwin = prof.newwin
        else:
            newwin = False

        page_root = '/users/u/' + self.user.username + '/arguments/' + self.kwargs['aset']
        context.update({'newwin': newwin,
                        'title': self.title,
                        'aset': self.kwargs['aset'],
                        'username': self.user,
                        'page_root': page_root})
        return context

class MessageList(ListView):
    
    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, *args, **kwargs):
        return super(MessageList, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return tcdMessage.objects.filter(recipient=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super(MessageList, self).get_context_data(**kwargs)
        page_root = '/users/messages/page'
        context.update({'page_root': page_root})
        return context


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

class RepliesView(ListView):
    
    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, *args, **kwargs):
        return super(RepliesView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        new_replies = fcomMessage.objects.filter(recipient=self.request.user)
        return new_replies
    
    def get_context_data(self, **kwargs):
        context = super(RepliesView, self).get_context_data(**kwargs)
        context.update({'username': self.request.user,
                        'page_root': '/users/replies'})
        return context

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
                          
@login_required(login_url='/users/login/')
def profile_stgs(request):
    """ Display the users current settings and allow them to be modified """
    user = request.user
    prof = get_object_or_404(Profile, user=user)
    
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
    redirect_to = '/users/settings/'
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

    redirect = '/users/messages/'
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
