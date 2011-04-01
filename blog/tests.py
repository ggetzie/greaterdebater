from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from blog.models import Blog, Post, PostComment
from comments.models import TopicComment, Debate
from items.models import Topic, Tags
from profiles.models import Profile
from testsetup import testsetup, create_user, create_topic, create_tcomment

import datetime

class ViewTest(TestCase):
    
    def setUp(self):
        testsetup()

    def test_main(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        bad_user = User.objects.exclude(id=user.id)[0]

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_post_detail(self):
        blog = Blog.objects.all()[0]
        user = blog.author
        bad_user = User.objects.exclude(id=user.id)[0]
        post = blog.post_set.filter(draft=False)[0]
        url = '/blog/%s/post/%i/' % (user.username, post.id)

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_addcomment(self):
        blog = Blog.objects.all()[0]
        user = blog.author
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/' % user.username
        pass
    
    def test_archive(self):
        user = Blog.objects.all()[0].author
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/archive' % user.username

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_about(self):
        user = Blog.objects.all()[0].author
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/about/' % user.username

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_new_post(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        pass
    
    def test_edit_post(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/drafts/' % user.username
        pass
    
    def test_show_drafts(self):
        user = Blog.objects.all()[0].author
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/drafts/' % user.username

        # not logged in
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    
    def test_save_draft(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        pass
    
    def test_preview(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        pass
    
    def test_publish(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        pass
    
    def test_delete(self):
        user = Blog.objects.all()[0].author
        url = '/blog/%s/' % user.username
        pass
        
