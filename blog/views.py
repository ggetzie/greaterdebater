from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tcd.blog.models import Post, PostComment
from tcd.blog.forms import PostEdit
from tcd.comments.utils import build_list

def main(request, username):
    # show five most recent posts
    # with titles and first few lines
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    five = blog.post_set.objects.filter(draft=False).order_by('-pub_date')[:5]    
    return render_to_response('blog/main.html',
                              {'topfive': five},
                              context_instance=RequestContext(request))

def post_detail(request, username, id):
    # show a single post
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=id)
    comments = build_list(post.PostComment_set.all(), 0)
    return render_to_response('blog/post_detail.html',
                              {'post': post,
                               'comments': comments},
                              context_instance=RequestContext(request))

def new_post(request):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        blog = get_object_or_404(blog, author=user)
        form = PostEdit()
        return render_to_response('blog/newpost.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def upload_post(request):
    pass

def save_draft(request, username):    
    user = get_object_or_404(User, username=username)
    if request.user == user:
        if request.POST:
            form = PostEdit(request.POST):
            if form.is_valid():
                pass
            else:
                msg = "Invalid Form"
        else:
            msg = "Not a Post"
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")


def drafts(request):
    pass

def comment(request):
    # add a comment
    pass

def edit_post(request):
    pass

def publish(request):
    pass
