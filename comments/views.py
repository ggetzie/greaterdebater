from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import loader, RequestContext, Context
from django.utils.http import urlquote_plus, urlquote
from django.views.generic.list import ListView

from forms import CommentForm, DeleteForm, FollowForm
from models import ArgComment, TopicComment, Debate, fcomMessage
from utils import build_list

from items.models import Topic
from items.forms import Flag

from profiles.models import Profile

from base_utils import calc_start, render_to_AJAX, render_message

import datetime

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
    # Only logged-in users can comment
    if not request.user.is_authenticated():
        redirect_to = ''.join(['/users/login/?next=/', str(topic_id), '/'])
        return HttpResponseRedirect(redirect_to)

    # Only POST requests are valid
    if not request.POST:
        messages.error(request, "Not a POST")
        return HttpResponseRedirect(redirect_to)

    # Validate the form
    form=CommentForm(request.POST)
    if not form.is_valid():
        message = "<p>Oops! A problem occurred.</p>"
        messages.error(request, message+str(form.errors))
        return HttpResponseRedirect(redirect_to)

    # Check if this user has exceeded the rate limit for posting
    prof = get_object_or_404(Profile, user=request.user)
    ratemsg = prof.check_rate()
    if ratemsg:
        messages.info(request, ratemsg)
        return HttpResponseRedirect(redirect_to)    
    
    # Save the comment
    top = get_object_or_404(Topic, pk=topic_id)
    params = {'comment': form.cleaned_data['comment'],
              'user': request.user,
              'ntopic': top,
              'needs_review': prof.probation, # Comments from probationary users must be reviewed
              'spam': prof.shadowban # ignore comments from known spammers
              }
    if form.cleaned_data['toplevel'] == 1:
        params['nparent_id'] = 0
        params['nnesting'] = 10
    else:
        params['nparent_id'] = form.cleaned_data['parent_id']
        params['nnesting'] = form.cleaned_data['nesting'] + 40
    c = TopicComment(**params)
    c.save()
    
    if prof.probation:
        messages.info(request, "Thank you. Your comment will appear after a brief review.")

    if prof.followcoms: 
        c.followers.add(request.user)
        c.save()

    # alert topic or comment followers of a new reply
    if not (c.needs_review or c.spam):
        if c.nparent_id == 0:
            followers = top.followers.all()
        else:
            parent = TopicComment.objects.get(id=c.nparent_id)
            followers = parent.followers.all()

        for follower in followers:
            msg = fcomMessage(recipient=follower,
                              is_read=False,
                              reply=c,
                              pub_date=datetime.datetime.now())
            msg.save()

        top.comment_length += len(c.comment)
        top.recalculate()
        top.save()

    prof.last_post = c.pub_date
    prof.save()

    return HttpResponseRedirect(redirect_to)    
                    
def edit(request, topic_id):
    redirect_to = '/' + topic_id + '/'
    if not request.user.is_authenticated():
        return HttpResponseRedirect(redirect_to)
    
    if not request.POST:
        messages.error(request, "Not a POST")
        return HttpResponseRedirect(redirect_to)

    form=CommentForm(request.POST)
    if not form.is_valid():
        message = "<p>Oops! A problem occurred.</p>"
        messages.error(request, message+str(form.errors))
        return HttpResponseRedirect(redirect_to)

    # parent_id is the id of the comment being edited
    # This is so we can reuse the same form for edits as for reply
    c = get_object_or_404(TopicComment, pk=form.cleaned_data['parent_id'])
    if c.user != request.user:
        messages.error(request, "<p>Can't edit another user's comment!</p>")
        return HttpResponseRedirect(redirect_to)

    # Adjust the score for the topic based on the new comment length
    top = c.ntopic
    deltalen = len(form.cleaned_data['comment']) - len(c.comment)
    top.comment_length += deltalen
    top.recalculate()
    top.save()

    # save the edited version of the comment
    c.comment = form.cleaned_data['comment']
    c.last_edit = datetime.datetime.now()
    c.save()
    return HttpResponseRedirect(redirect_to)
                                
def delete(request):
    """Unpermanently deletes a comment, undeletes a comment that has been deleted"""
    redirect_to = '/'
    if not request.POST:
        return render_to_AJAX(status="error",
                              messages=[render_message(message="Not a POST", nesting=10)])
            
    form=DeleteForm(request.POST)
    if not form.is_valid():
        return render_to_AJAX(status="alert",
                              messages=["Invalid Form"])

    try:
        comment = TopicComment.objects.get(pk=form.cleaned_data['comment_id'])
    except TopicComment.DoesNotExist:
        return render_to_AJAX(status="alert",
                              messages=["Comment Not Found"])

    if not comment.user == request.user:
        return render_to_AJAX(status="alert",
                              messages=["Can't delete a comment that isn't yours"])

    # Can't delete a comment if there are any 
    # debates associated with it
    debs = Debate.objects.filter(incite=comment)
    if debs:
        return render_to_AJAX(status="error",
                              messages=[render_message(
                    message="Can't delete a comment that has debates", nesting=10),
                                        str(comment.id)])

    top = comment.ntopic
    # Toggle the deleted state of the comment
    if comment.removed:
        comment.removed = False
        top.comment_length += len(comment.comment)                        
    else:
        comment.removed = True
        top.comment_length -= len(comment.comment)                        
    top.recalculate()
    top.save()
    comment.save()
    comt = loader.get_template('comments/one_comment.html')                
    comc = Context({'comment': comment,
                    'user': request.user})
    return render_to_AJAX(status='ok',
                          messages=[comt.render(comc),
                                    str(comment.id)])
                                    
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
    comment = get_object_or_404(TopicComment, pk=comment_id)

    if 'context' in request.GET:
        try:
            context = int(request.GET['context'])
        except ValueError:
            context=1
        for i in range(context):
            if comment.nparent_id == 0: break
            comment = get_object_or_404(TopicComment, pk=comment.nparent_id)
    
    comtree = [comment]
    comtree.extend(build_list(TopicComment.objects.filter(ntopic=comment.ntopic,
                                                          needs_review=False, first=False),
                              comment.id))
    if request.user.is_authenticated():
        prof = get_object_or_404(Profile, user=request.user)
        newwin = prof.newwin
    else:
        newwin = False
    
    return render_to_response("items/topic_detail.html",
                              {'rest_c': comtree, 
                               'object': comment.ntopic, 
                               'onecom': True,
                               'newwin': newwin,
                               'com': int(comment_id),
                               'rootnest': comtree[0].nnesting},
                              context_instance=RequestContext(request))

class CommentDebateList(ListView):

    def get_queryset(self):
        self.comment = get_object_or_404(TopicComment, pk=self.kwargs['comment_id'])
        args_list = Debate.objects.filter(incite=self.comment, status__range=(1,5)).order_by('-start_date')
        return args_list
    
    def get_context_data(self, **kwargs):
        context = super(CommentDebateList, self).get_context_data(**kwargs)
        context.update({'comment': self.comment,
                        'page_root': '/comments/%i/arguments' % self.comment.id})
        return context
                                    
                                    
def flag(request):
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
        com = TopicComment.objects.get(pk=form.cleaned_data['object_id'])
    except TopicComment.DoesNotExist:
        message = render_message("Object not found", 10)
        return render_to_AJAX(status="alert",
                              messages=[message])
    user = request.user
    if user in com.cflaggers.all():
        message="You've already flagged this comment"
    else:
        com.cflaggers.add(user)
        if com.cflaggers.count() > 10 or user.is_staff:
            com.needs_review = True
            # remove this comment's length from the score
            # for this topic
            top = com.ntopic
            top.comment_length -= len(com.comment)
            top.recalculate()
            top.save()

        com.save()
        message="Comment flagged"

    return render_to_AJAX(status="ok",
                          messages=[render_message(message, com.nnesting)])

def toggle_follow(request):
    status = "error"
    if not request.user.is_authenticated(): return render_to_AJAX(status="error", 
                                                                  messages=[render_message("Not logged in", 10)])

    if not request.POST: return render_to_AJAX(status="error", 
                                               messages=[render_message("Not a POST", 10)])
    
    form = FollowForm(request.POST)
    if not form.is_valid(): return render_to_AJAX(status="error", 
                                               messages=[render_message("Invalid Form", 10)])
    nesting = 10
    try:
        itemmap = {"Topic": Topic,
                   "TopicComment": TopicComment}
        itemmodel = itemmap[form.cleaned_data['item']]
        id = form.cleaned_data['id']
        item = itemmodel.objects.get(pk=id)
        if itemmodel == TopicComment: nesting = item.nnesting

        if request.user in item.followers.all():
            item.followers.remove(request.user)
            message = "off"
        else:
            item.followers.add(request.user)
            message = "on"
        item.save()
        status = "ok"
    except ObjectDoesNotExist:
        message = "Item not found"
        status = "alert"
    except KeyError:
        message = "No items of type %s" % form.cleaned_data['item']
        status = "alert"
            
    return render_to_AJAX(status=status,
                          messages=[message])
