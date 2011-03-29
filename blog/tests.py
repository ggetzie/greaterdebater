from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from blog.models import Blog, Post, PostComment
from comments.models import TopicComment, Debate
from items.models import Topic, Tags
from profiles.models import Profile, 
from testsetup import testsetup, create_user, create_topic, create_tcomment

import datetime

class ViewTest(TestCase):
    
    def setUp(self):
        testsetup()

    def test_main(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_post_detail(self):
        blog = Blog.objects.all()[0]
        user = blog.user
        post = blog.post_set.all()[0]
        url = '/blog/%s/%i/' % (user.username, post.id)
        pass
    
    def test_addcomment(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_archive(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_about(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass

    def test_new_post(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_edit_post(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_show_drafts(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_save_draft(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_preview(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_publish(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
    
    def test_delete(self):
        user = Blog.objects.all()[0].user
        url = '/blog/%s/' % user.username
        pass
        
