from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context, RequestContext
from django.views.generic.list import ListView

from tcd.blog.models import Blog, Post, PostComment
from tcd.blog.forms import PostEdit, PostCommentForm, PostNew, UploadFileForm
from tcd.comments.utils import build_list
from tcd.profiles.models import Profile
from settings import UPLOAD_DIR
from tcd.utils import render_to_AJAX, render_message
from blog.utils import get_user_path

import datetime
import os
import hashlib

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
    blog = get_object_or_404(Blog, author__username=username)
    post = get_object_or_404(Post, id=id)
    # comments = post.postcomment_set.filter(needs_review=False,
    #                                     spam=False).order_by('-pub_date')
    
    return render_to_response('blogtemplates/post_detail.html',
                              {'post': post,
                               'blog': blog,
                               # 'comments': comments,
                               'comments': [],
                               'pcform': PostCommentForm(initial={'post_id': post.id}),
                               'show_post': not post.draft or request.user == blog.author,
                               },
                              
                              context_instance=RequestContext(request))

def addcomment(request, username):
    blog = get_object_or_404(Blog, author__username=username)
    redirect_to = '/blog/%s/' % username

    if not request.POST:
        messages.error(request, "Not a POST")
        return HttpResponseRedirect(redirect_to)

    if not request.user.is_authenticated():
        redirect_to = '/users/login?next=/blog/'+ username + '/'
        return HttpResponseRedirect(redirect_to)

    prof = get_object_or_404(Profile, user=request.user)
    form = PostCommentForm(request.POST)
    if not form.is_valid():
        message = "<p>Oops! A problem occurred.</p>"
        messages.error(request, message+str(form.errors))
        return HttpResponseRedirect(redirect_to)

    post = get_object_or_404(Post, id=form.cleaned_data['post_id'])
    redirect_to = '/blog/%s/post/%i/' % (username, post.id)

    ratemsg = prof.check_rate()
    if ratemsg:
        messages.info(request, ratemsg)
        return HttpResponseRedirect(redirect_to)

    comment = PostComment(blog=blog,
                          post=post,
                          user=request.user,
                          comment=form.cleaned_data['comment'],
                          needs_review=prof.probation)
    comment.save()

    prof.last_post = comment.pub_date
    prof.save()
    if prof.probation:
        messages.info(request, "Thank you! Your comment will appear after a brief review.")
    return HttpResponseRedirect(redirect_to)

class ArchiveView(ListView):
    
    def get_queryset(self):
        self.blog = get_object_or_404(Blog, author__username=self.kwargs['username'])
        posts = self.blog.post_set.filter(draft=False).order_by('-pub_date')
        return posts

    def get_context_data(self, **kwargs):
        context = super(ArchiveView, self).get_context_data(**kwargs)
        context.update({'blog': self.blog,
                        'page_root': '/blog/%s/archive' % self.blog.author.username})
        return context

def about(request, username):
    return render_to_response('blogtemplates/about.html',
                              {'blog': get_object_or_404(Blog, author__username=username)},
                              context_instance=RequestContext(request))

def new_post(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user == user:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")
    blog = get_object_or_404(Blog, author=user)
    if request.POST:
        form = PostNew(request.POST)
        if form.is_valid():
            post = Post(title=form.cleaned_data['title'],
                        txt=form.cleaned_data['txt'],
                        tags=form.cleaned_data['tags'],
                        created=datetime.datetime.now(),
                        blog=blog)
            post.save()
            redirect_to = ''.join(['/blog/', blog.author.username, '/edit/', str(post.id)])
            return HttpResponseRedirect(redirect_to)
    else:
        form = PostNew({'title': "Untitled Post",
                        'txt': "Enter text here"})

    return render_to_response('blogtemplates/post_new.html',
                              {'form': form,
                               'blog': blog},
                              context_instance=RequestContext(request))

        
def edit_post(request, username, id):
    # Display the post for editing

    user = get_object_or_404(User, username=username)
    if not request.user.is_authenticated():
        return HttpResponseForbidden("<h1>Unauthorized</h1>")
    
    if not request.user == user:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")

    blog = get_object_or_404(Blog, author=user)
    post = get_object_or_404(Post, id=id)

    data = {'title': post.title,
            'tags': post.tags,
            'txt': post.txt,
            'id': post.id}

    form = PostEdit(data)

    return render_to_response('blogtemplates/post_edit.html',
                              {'form': form,
                               'blog': blog,
                               'post': post},
                              context_instance=RequestContext(request))

def show_drafts(request, username):
    """Show all unpublished drafts"""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        blog = get_object_or_404(Blog, author=user)
        drafts = blog.post_set.filter(draft=True).order_by('-created')
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

    if not request.POST:
        msgs = [render_message("Not a POST", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    if not request.user.is_authenticated():
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    if not request.user == user:
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    form = PostEdit(request.POST)
    if not form.is_valid():
        msgs = [render_message("Invalid Form", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    post = Post.objects.get(pk=form.cleaned_data['id'])
    post.txt = form.cleaned_data['txt']
    post.tags = form.cleaned_data['tags']
    post.title = form.cleaned_data['title']
    post.save()

    msgs = [render_message("Draft Saved", 10)]
    return render_to_AJAX(status="ok", messages=msgs)

def preview(request, username):
    blog = Blog.objects.get(author__username=username)
    user = blog.author

    if not request.POST:
        msgs = [render_message("Not a POST", 10)]
        return render_to_AJAX(status="error",
                              messages=msgs)

    if not request.user.is_authenticated():
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    if not request.user == user:
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    form = PostEdit(request.POST)
    if not form.is_valid():
        msgs = [render_message("Invalid Form", 10)]
        return render_to_AJAX(status="error", messages=msgs)
                              

    post = get_object_or_404(Post, id=form.cleaned_data['id'])
    post.txt = form.cleaned_data['txt']
    post.tags = form.cleaned_data['tags']
    post.title = form.cleaned_data['title']
    post.save()
    msgs = [render_message("Changes Saved", 10)]
    return render_to_AJAX(status="ok",
                          messages=msgs)

def publish(request, username):
    """Make the post available for public viewing"""
    user = get_object_or_404(User, username=username)
    blog = Blog.objects.get(author__username=username)

    if not request.POST:
        msgs = [render_message("Not a POST", 10)]
        return render_to_AJAX(status="error",
                              messages=msgs)

    if not request.user.is_authenticated():
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    if not request.user == user:
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    data = request.POST.copy()
    form = PostEdit(data)

    if not form.is_valid():
        msgs = [render_message("Invalid Form", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    post = get_object_or_404(Post, id=form.cleaned_data['id'])
    post.draft = False
    post.pub_date = datetime.datetime.now()
    post.txt = form.cleaned_data['txt']
    post.tags = form.cleaned_data['tags']
    post.title = form.cleaned_data['title']
    post.save()

    msgs = [render_message("Post published", 10)]
    return render_to_AJAX(status="ok", messages=msgs)

def delete(request, username):
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)

    if not request.POST:
        msgs = [render_message("Not a POST", 10)]
        return render_to_AJAX(status="error",
                              messages=msgs)

    if not request.user.is_authenticated():
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)

    if not request.user == user:
        msgs = [render_message("Unauthorized", 10)]
        return render_to_AJAX(status="error", messages=msgs)
    
    data = request.POST.copy()
    post = get_object_or_404(Post, id=data['id'])
    post.delete()
    status = 'ok'
    msgs = [render_message("Post Deleted", 10)]
    return render_to_AJAX(status="ok", messages=msgs)

@login_required(login_url='/users/login/')
def myfiles(request, username):
    blog = get_object_or_404(Blog, author__username=username)
    userpath = get_user_path(request.user.username)
    if not os.path.isdir(userpath):
        os.makedirs(userpath, 0777)
    flist = os.listdir(userpath)
    section = os.path.dirname(userpath)[-4:]
    url_path = 'upload/%s/%s/' % (section, username)
    return render_to_response('blogtemplates/myfiles.html',
                              {'file_list': flist,
                               'userpath': url_path,
                               'blog': blog},
                              context_instance=RequestContext(request))

@login_required(login_url='/users/login/')    
def upload_file(request, username):
    blog = get_object_or_404(Blog, author__username=username)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.user, request.FILES['file'])
            return HttpResponseRedirect('/blog/%s/myfiles/' % request.user.username)
    else:
        form = UploadFileForm()
    return render_to_response('blogtemplates/upload.html', {'form': form,
                                                            'blog': blog},
                              context_instance=RequestContext(request))

def handle_uploaded_file(user, ufile):

    userpath = get_user_path(user.username)
    if not os.path.isdir(userpath):
        os.makedirs(userpath, 0777)

    destination = open(os.path.join(userpath, ufile.name), 'wb+')
    for chunk in ufile.chunks():
        destination.write(chunk)
    destination.close()
    section = os.path.dirname(userpath)[-4:]
    return '/static/upload/%s/%s/%s' % (section, user.username, ufile.name)

