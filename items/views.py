from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from tcd.items.models import Topic
from tcd.comments.models import Comment
from tcd.comments.forms import CommentForm
import datetime

def comments(request, topic_id):
    top = get_object_or_404(Topic, pk=topic_id)
    comments = top.comment_set
    first_c = comments.filter(is_first=True)
    rest_c = comments.filter(is_first=False)
    next = request.path
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
                                                          'next': next,
                                                          'form_comment': form_comment
                                                          })

def add(request, topic_id):
    top = get_object_or_404(Topic, pk=topic_id)
    com = Comment(comment=request.POST['comment_text'],
                  user=request.user,
                  pub_date=datetime.datetime.now(),
                  topic=top)
    com.save()
    return HttpResponseRedirect(reverse('tcd.items.views.comments', args=(topic_id)))
