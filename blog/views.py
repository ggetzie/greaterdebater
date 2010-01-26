from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context, RequestContext

from tcd.blog.models import Blog, Post, PostComment
from tcd.blog.forms import PostEdit
from tcd.comments.utils import build_list

import pyfo
import datetime

def main(request, username):
    # show five most recent posts
    # with titles and first few lines
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    five = blog.post_set.filter(draft=False).order_by('-pub_date')[:5]    
    return render_to_response('blogtemplates/main.html',
                              {'topfive': five,
                               'blog': blog},
                              context_instance=RequestContext(request))

def post_detail(request, username, id):
    # show a single post
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    post = get_object_or_404(Post, id=id)
    comments = build_list(post.postcomment_set.all(), 0)
    return render_to_response('blogtemplates/post_detail.html',
                              {'post': post,
                               'blog': blog,
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
                        txt="Enter text here",
                        created=datetime.datetime.now(),
                        blog=blog)
            
        data = {'title': post.title,
                'tags': post.tags,
                'txt': post.txt}
        form = PostEdit(data)

        return render_to_response('blogtemplates/post_edit.html',
                                  {'form': form,
                                   'blog': blog,
                                   'post': post},
                                  context_instance=RequestContext(request))
    else:
        return HttpReponseForbidden("<h1>Unauthorized</h1>")

def show_drafts(request, username):
    """Show all unpublished drafts"""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        blog = get_object_or_404(Blog, author=user)
        drafts = blog.post_set.filter(draft=True)
        return render_to_response('blogtemplates/drafts.html',
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
    blog = get_object_or_404(Blog, author=user)
    status = 'error'
    if request.user == user:
        if request.POST:
            form = PostEdit(request.POST)
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
                                created = datetime.datetime.now(),
                                blog=blog)
                post.save()
                msg = "Draft Saved"
                status = 'ok'
            else:
                msg = "Invalid Form"
        else:
            msg = "Not a Post"
    else:
        msg = "Unauthorized"
    msgt = loader.get_template('sys_msg.html')
    msgc = Context({'message': msg,
                    'nesting': 10})
    
    message = msgt.render(msgc)
    
    xmlcontext = Context({'status': status,
                          'messages': [message]})
    rtemp = loader.get_template("AJAXresponse.xml")
    response = rtemp.render(xmlcontext)

    return HttpResponse(response)

def publish(request, username):
    """Make the post available for public viewing"""
    user = get_object_or_404(User, username=username)
    status = 'error'
    if request.user == user:
        if request.POST:
            data = request.POST.copy()
            form = PostEdit(data)
            if form.is_valid():
                try:
                    post = get_object_or_404(Post, id=form.cleaned_data['id'])
                    post.draft = False
                    post.pub_date = datetime.datetime.now()
                    post.save()
                    msg = "Post published"
                    status = 'ok'
                except KeyError:
                    msg = "Invalid id"
            else:
                msg = "Invalid Form"
        else:
            msg = "Not a Post"
    else:
        msg = "Unauthorized"

    msgt = loader.get_template('sys_msg.html')
    msgc = Context({'message': msg,
                     'nesting': 10})
    message = msgt.render(msgc)

    xmlcontext = Context({'status': status,
                          'messages': [message]})
    rtemp = loader.get_template('AJAXresponse.xml')
    response = rtemp.render(xmlcontext)
    return HttpResponse(response)


def comment(request):
    # add a comment
    pass
