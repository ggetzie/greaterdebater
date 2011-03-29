from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context, RequestContext
from django.views.generic import list_detail

from tcd.blog.models import Blog, Post, PostComment
from tcd.blog.forms import PostEdit, PostCommentForm, PostNew
from tcd.comments.utils import build_list
from tcd.profiles.models import Profile
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
    blog = get_object_or_404(Blog, author__username=username)
    post = get_object_or_404(Post, id=id)
    comments = post.postcomment_set.filter(needs_review=False,
                                           spam=False).order_by('-pub_date')
    
    return render_to_response('blogtemplates/post_detail.html',
                              {'post': post,
                               'blog': blog,
                               'comments': comments,
                               'pcform': PostCommentForm(initial={'post_id': post.id}),
                               'show_post': not post.draft or request.user == blog.author,
                               },
                              
                              context_instance=RequestContext(request))

def addcomment(request, username):
    blog = get_object_or_404(Blog, author__username=username)
    redirect_to = blog.get_absolute_url()

    if not request.user.is_authenticated():
        redirect_to = '/login?next=' + blog.get_absolute_url() + 'post/' +  str(post.id) + '/'
        return HttpResponseRedirect(redirect_to)

    if not request.POST:
        messages.error(request, "Not a POST")
        return HttpResponseRedirect(redirect_to)

    prof = get_object_or_404(Profile, user=request.user)
    form = PostCommentForm(request.POST)
    post = get_object_or_404(Post, id=request.POST['post_id'])
    redirect_to = ''.join([blog.get_absolute_url(), 'post/', str(post.id)])
    if not form.is_valid():
        message = "<p>Oops! A problem occurred.</p>"
        messages.error(request, message+str(form.errors))
        return HttpResponseRedirect(redirect_to)
           
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

def archive(request, username, page=1):
    paginate_by = 15
    blog = get_object_or_404(Blog, author__username=username)
    posts = Post.objects.filter(blog=blog, draft=False).order_by('-pub_date')

    return list_detail.object_list(request=request, 
                                   queryset=posts,
                                   paginate_by = paginate_by,
                                   page=page,
                                   template_name="blogtemplates/archive.html",
                                   template_object_name="post",
                                   extra_context={'blog': blog})

def about(request, username):
    return render_to_response('blogtemplates/about.html',
                              {'blog': get_object_or_404(Blog, author__username=username)},
                              context_instance=RequestContext(request))

def new_post(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
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
    else:
        return HttpResponseForbidden("<h1>Unauthorized</h1>")
                                   

        
def edit_post(request, username, id):
    user = get_object_or_404(User, username=username)
    if request.user == user:
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
    else:
        return HttpReponseForbidden("<h1>Unauthorized</h1>")

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
    status = 'error'
    if request.user == user:
        if request.POST:
            form = PostEdit(request.POST)
            if form.is_valid():

                post = Post.objects.get(pk=form.cleaned_data['id'])
                post.txt = form.cleaned_data['txt']
                post.tags = form.cleaned_data['tags']
                post.title = form.cleaned_data['title']

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
    
    xmlc = Context({'status': status,
                    'messages': [message]})
    xmlt = loader.get_template("AJAXresponse.xml")
    response = xmlt.render(xmlc)

    return HttpResponse(response)

def preview(request, username):
    blog = Blog.objects.get(author__username=username)
    status="error"
    if request.POST:
        form = PostEdit(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, id=form.cleaned_data['id'])
            post.txt = form.cleaned_data['txt']
            post.tags = form.cleaned_data['tags']
            post.title = form.cleaned_data['title']
            post.save()
            status = "ok"
            msg = "Changes Saved"
        else:
            msg = "Invalid Form"
    else:
        msg = "Not a Post"

    msgt = loader.get_template('sys_msg.html')
    msgc = Context({'message': msg,
                    'nesting': 10})

    xmlt = loader.get_template('AJAXresponse.xml')
    xmlc = Context({'status': status,
                    'messages': [msgt.render(msgc)]})

    response = xmlt.render(xmlc)
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
                    post.txt = form.cleaned_data['txt']
                    post.tags = form.cleaned_data['tags']
                    post.title = form.cleaned_data['title']
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

def delete(request, username):
    user = get_object_or_404(User, username=username)
    blog = get_object_or_404(Blog, author=user)
    status = 'error'
    if request.user == blog.author:
        if request.POST:
            data = request.POST.copy()
            post = get_object_or_404(Post, id=data['id'])
            post.delete()
            status = 'ok'
            msg = "Post Deleted"
        else:
            msg = "Not a POST"
    else:
        msg = "Unauthorized"
    if status == 'error':
        msgt = loader.get_template('sys_msg.html')
        msgc = Context({'message': msg,
                        'nesting': 10})
        message = msgt.render(msgc)
    else:
        message = msg
    xmlt = loader.get_template('AJAXresponse.xml')
    xmlc = Context({'status': status,
                    'messages': [message]})
    response = xmlt.render(xmlc)
    return HttpResponse(response)
    

