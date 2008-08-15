from django import oldforms as forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.views.generic import list_detail

from tcd.comments.forms import CommentForm
from tcd.comments.models import *
from tcd.items.forms import *
from tcd.items.models import *
from tcd.utils import *
import datetime

def comments(request, topic_id, page=1):
    paginate_by = 100
    has_previous = False
    has_next = True
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.comment_set.filter(is_msg=False, 
                                      arg_proper=False)
    first_c = comments.filter(is_first=True)
    rest_c = build_list(comments.filter(is_first=False), 0)
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
    except:
        has_next = False

    return render_to_response('items/topic_detail.html', 
                              {'object': top,
                               'first_c': first_c,
                               'rest_c': rest_c,
                               'rest_c': rest_c[start:end],
                               'redirect': ''.join(["/", str(topic_id), "/"]),
                               'has_previous': has_previous,
                               'previous': previous,
                               'has_next': has_next,
                               'next': next,
                               'form_comment': form_comment},
                              context_instance=RequestContext(request)
                              )

def topics(request, page=1):
    paginate_by = 25
    if page == 'last':
        start = paginate_by * (Topic.objects.count() / paginate_by) + 1
    else:
        start = paginate_by * (int(page) - 1) + 1        
    user = request.user
    if user.is_authenticated() and tcdMessage.objects.filter(recipient=user, is_read=False):        
        user.message_set.create(message=''.join(["<a href='/", user.username,
                                                 "/messages/'>You have unread messages</a>"]))
    return list_detail.object_list(request=request, 
                                   queryset=Topic.objects.all(), 
                                   paginate_by=paginate_by, 
                                   page=page,
                                   extra_context={'start': start,})

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
                               'redirect' : next})

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
                               'redirect': next,
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
                              sub_date=datetime.datetime.now(),
                              comment_length=0,
                              last_calc=datetime.datetime.now())
                topic.save()
                next = ''.join(["/", str(topic.id), "/"])
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
                                  {'redirect': '/submit/',
                                   'message': "Please log in to submit a topic",
                                   'form': tcdLoginForm()},
                                  context_instance=RequestContext(request))

def edit_topic(request, topic_id):
    top = get_object_or_404(Topic, pk=topic_id)
    c = Comment.objects.filter(topic=top, is_first=True)
    redirect = ''.join(['/', request.user.username, '/submissions/'])    
    if request.user == top.user and request.method == 'POST':
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
            if form.cleaned_data['url']:
                if top.url[0:4] == 'http':
                    top.url = form.cleaned_data['url']
                else:
                    request.user.message_set.create(message="Can't change url of self-referential topic.")
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
                               'username': top.user.username},
                              context_instance=RequestContext(request))
        
def challenge(request, c_id):
    if request.POST:
        form = CommentForm(request.POST)
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
                                   title= ''.join([c.comment[:20].replace('\r', ' '), '...']),
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
        request.user.message_set.create(message="wtf not a POST")
        redirect = '/'
    return HttpResponseRedirect(redirect)

def rebut(request, a_id):
    if request.POST:
        form = CommentForm(request.POST)
        arg = get_object_or_404(Argument, pk=a_id)
        redirect = ''.join(['/argue/', str(arg.id), '/'])
        if form.is_valid():            
            if arg.whos_up() == request.user:
                if arg.status == 2:
                    arg.status = 1
                elif arg.status == 1:
                    arg.status = 2
                elif arg.status == 0:
                    arg.status = 1
                else:
                    request.user.message_set.create(message="Argument not active!")
                    return HttpResponseRedirect(redirect)                
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
                request.user.message_set.create(message="Argument Rebutted!")
            else:
                request.user.message_set.create(message="Not your turn")
        else:
            request.user.message_set.create(message="Invalid form")
    else:
        request.user.message_set.create(message="wtf not a POST")
        redirect = '/'
    return HttpResponseRedirect(redirect)

def respond(request, response, a_id):
    """Potential opponent accepts or rejects a challenge to an argument."""    
    arg = get_object_or_404(Argument, pk=a_id)
    if request.user == arg.defendant:
        redirect = ''.join(["/argue/", str(arg.id), "/"])
        if arg.status == 0:
            if response == 'accept':
                arg.status = 2
                message = ''.join([arg.defendant.username, 
                                   " has accepted your challenge. \n[View this argument](", redirect, ")"])
                msg = tcdMessage(user=request.user,
                                 recipient=arg.plaintiff,
                                 comment=message,
                                 subject="Challenge accepted",
                                 parent_id=0,
                                 pub_date=datetime.datetime.now(),
                                 nesting=0)
                msg.save()
                
            elif response == 'decline':
                arg.status = 6
                message = ''.join([ arg.defendant.username, 
                                    " has declined your challenge."])
                msg = tcdMessage(user=request.user,
                                 recipient=arg.plaintiff,
                                 comment=message,
                                 subject="Challenge declined",
                                 parent_id=0,
                                 nesting=0)
                msg.save()
            else:
                request.user.message_set.create(message="Badly formed URL")
        else:
            request.user.message_set.create(message="Challenge already accepted or declined")
    else:
        request.user.message_set.create(message="Can't respond to a challenge that's not for you!")

    arg.save()
    return HttpResponseRedirect(redirect)

def draw(request, a_id):
    arg = Argument.objects.get(pk=a_id)
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
        request.user.message_set.create(message=''.join(["Offered a draw to ", recipient.username]))
        return rebut(request, a_id)
    else:
        request.user.message_set.create(message="Not your turn, not your argument, or there's already a draw offer outstanding")
    return HttpResponseRedirect(redirect)

def respond_draw(request, response, a_id):
    arg = Argument.objects.get(pk=a_id)
    draw = Draw.objects.get(argument=arg)
    redirect = ''.join(["/argue/", str(arg.id), "/"])
    if request.user == draw.recipient:
        if response == "accept":
            message = ''.join([request.user.username, " has accepted your offer of a draw",
                               " regarding \n[", arg.title, "](", redirect, ")"])
            subject = "Draw Accepted"
            request.user.message_set.create(message="Accepted draw")
            arg.status = 5            
        elif response == "decline":
            message = ''.join([request.user.username, " has declined your offer of a draw",
                               " regarding \n[", arg.title, "](", redirect, ")"])
            subject = "Draw Declined"
            request.user.message_set.create(message="Draw Rejected")
        else:
            request.user.message_set.create(message="Badly formed URL")
            return HttpResponseRedirect(redirect)
        msg = tcdMessage(user=request.user,
                             recipient = draw.offeror,
                             comment = message,
                             subject = subject,
                             parent_id = 0,
                             nesting = 0)
        draw.delete()
        msg.save()
        arg.save()
    return HttpResponseRedirect(redirect)

def concede(request, a_id):
    arg = Argument.objects.get(pk=a_id)
    redirect = ''.join(["/argue/", str(arg.id), "/"])
    if request.user in (arg.defendant, arg.plaintiff):
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
        request.user.message_set.create(message="Point conceded")
    else:
        request.user.message_set.create(message="Not your argument")
    return HttpResponseRedirect(redirect)

def profile(request, value):
    user = get_object_or_404(User, username=value)
    user_info = get_object_or_404(Profile, user=user)
    return render_to_response("registration/profile/profile_home.html",
                              {'username': user,
                               'user_info': user_info,},
                              context_instance=RequestContext(request))

def profile_args(request, value):
    user = get_object_or_404(User, username=value)
    args = user.defendant_set.all() | user.plaintiff_set.all()
    return render_to_response("registration/profile/profile_args.html",
                              {'username': user,
                               'args_list': args.order_by('start_date')},
                              context_instance=RequestContext(request))

def profile_msgs(request, value):
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

def object_list_field(request, model, field, value, paginate_by=None, page=None,
                      fv_dict={}, allow_empty=True, template_name=None, 
                      template_loader=loader, extra_context=None, context_processors=None,
                      template_object_name='object', mimetype=None):
    """Extends generic view object_list to display a list of objects filtered 
    by an arbitrary field.
    Works only for fields that are not ForeignKey or ManyToMany. 
    See object_list_foreign_field for ForeignKey fields"""

    fv_dict[field] = value
    obj_list = model.objects.filter(**fv_dict)
    return list_detail.object_list(request=request, queryset=obj_list, 
                                   paginate_by=paginate_by, page=page, 
                                   allow_empty=allow_empty, template_name=template_name,
                                   template_loader=template_loader, extra_context=extra_context,
                                   context_processors=context_processors,
                                   template_object_name=template_object_name,
                                   mimetype=mimetype)

def object_list_foreign_field(request, model, field, value, foreign_model,
                              foreign_field, fv_dict={},
                              paginate_by=None, page=None, allow_empty=True,
                              template_name=None, template_loader=loader,
                              extra_context=None, context_processors=None,
                              template_object_name='object', mimetype=None):
    """Generic view to display a list of objects filtered by an arbitary foreign key field"""

    foreign_obj = get_object_or_404(foreign_model, **{foreign_field: value})
    fv_dict[field] = foreign_obj.id
    obj_list = model.objects.filter(**fv_dict)
    return list_detail.object_list(request=request, queryset=obj_list, 
                                   extra_context={foreign_field: foreign_obj},
                                   paginate_by=paginate_by, page=page, 
                                   allow_empty=allow_empty, template_name=template_name,
                                   template_loader=template_loader, 
                                   context_processors=context_processors,
                                   template_object_name=template_object_name,
                                   mimetype=mimetype)

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

def arg_detail(request, object_id):
    arg = Argument.objects.get(pk=object_id)
    turn = False
    if request.user == arg.defendant and arg.status == 0:
        new_arg = True
    else:
        new_arg = False
    if request.user in [arg.defendant, arg.plaintiff]:
        participants = True
    else:
        participants = False
    last_c = arg.comment_set.order_by('-pub_date')[0]
    return render_to_response("items/arg_detail.html",
                              {'object': arg,
                               'new_arg': new_arg,
                               'participants': participants,
                               'last_c': last_c},
                              context_instance=RequestContext(request))


    
