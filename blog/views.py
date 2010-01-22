from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tcd.blog.models import Post, PostComment
from tcd.blog.forms import PostEdit
from tcd.comments.utils import build_list

import pyfo
import datetime

def main(request, username):
    # show five most recent posts
    # with titles and first few lines
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    five = blog.post_set.objects.filter(draft=False).order_by('-pub_date')[:5]    
    return render_to_response('blog/main.html',
                              {'topfive': five,
                               'blog': blog},
                              context_instance=RequestContext(request))

def post_detail(request, username, id):
    # show a single post
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    post = get_object_or_404(Post, id=id)
    comments = build_list(post.PostComment_set.all(), 0)
    return render_to_response('blog/post_detail.html',
                              {'post': post,
                               'comments': comments},
                              context_instance=RequestContext(request))

def edit_post(request, username, id=None):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        blog = get_object_or_404(Blog, author=user)
        if id:
            post = get_object_or_404(Post, id=id)
            
        else:
            post = Post(title="Untitled Post",
                        txt="Enter text here")
            post.save()

        form = PostEdit(id = post.id,
                            title = post.title,
                            tags = post.tags,
                            txt = post.txt)

        return render_to_resonpse('blog/post_edit.html',
                                  {'form': form,
                                   'blog': blog,
                                   'post': post},
                                  context_instance=RequestContext(request))
    else:
        return HttpReponseForbidden("<h1>Unauthorized</h1>")

def show_drafts(request):
    """Show all unpublished drafts"""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        blog = get_object_or_404(author=user)
        drafts = blog.post_set.filter(draft=True)
       return render_to_response('blog/drafts.html',
                                  {'drafts': drafts,
                                   'blog': blog},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

def upload_post(request):
    pass

def save_draft(request, username):   
    """Store the post in the database, but do not publish"""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        if request.POST:
            form = PostEdit(request.POST):
            if form.is_valid():
                if form.cleaned_data['id']:
                    post = Post.objects.get(pk=form.cleaned_data['id'])
                    post.txt = form.cleaned_data['txt']
                    post.tags = form.cleaned_data['tags']
                    post.title = form.cleaned_data['title']
                else:
                    post = Post(txt = form.cleaned_data['txt'],
                                tags = form.cleaned_data['tags'],
                                title = form.cleaned_data['title'],
                                draft = True,
                                created = datetime.datetime.now())
                post.save()
                msg = "Draft Saved"
            else:
                msg = "Invalid Form"
        else:
            msg = "Not a Post"
    else:
        msg = "Unauthorized"
    response = ('response', [('message', msg)])
    response = pyfo.pyfo(response, prolog=True, encoding='utf-8')
    return HttpResponse(response)

def toggle_publish(request, username):
    """Make the post available for public viewing"""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        if request.POST:
            data = request.POST.copy()
            try:
                post = get_object_or_404(Post, id=data['id'])
                post.draft = False
                post.save()
            except KeyError:
                msg = "Invalid id"
        else:
            msg = "Not a Post"
    else:
        msg = "Unauthorized"
    response = ('response', [('message', msg)])
    response = pyfo.pyfo(response, prolog=True, encoding='utf-8')
    return HttpResponse(response)



def comment(request):
    # add a comment
    pass




