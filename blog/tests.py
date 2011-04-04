from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from blog.models import Blog, Post, PostComment
from comments.models import TopicComment, Debate
from items.models import Topic, Tags
from profiles.models import Profile
from testsetup import testsetup, create_user, create_topic, create_tcomment

import datetime
import urllib

def reset_postlimit(prof):
    prof.rate = 0
    prof.last_post = datetime.datetime(month=1, day=1, year=1970)
    prof.save()

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
        bad_prof = Profile.objects.filter(probation=False).exclude(user__id=user.id)[0]
        bad_user = bad_prof.user
        url = '/blog/%s/addcomment/' % user.username
        post = blog.post_set.filter(draft=False)[0]
        redirect_to = '/blog/%s/' % user.username
        
        # GET request
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirect_to)
        self.assertContains(response, "Not a POST")

        # not logged in
        response = self.client.post(url, {'post_id': post.id,
                                          'comment': 'some comment'},
                                    follow=True)
        # why does the test server redirect this way?
        # it doesn't escape the slashes in the next parameter other times
        redirect_to = '/users/login/?next=%2Fblog%2F'+ user.username + '%2F'
        self.assertRedirects(response, redirect_to)

        # invalid form
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'post_id': '',
                                          'comment': ''},
                                    follow=True)
        redirect_to = '/blog/%s/' % user.username
        self.assertRedirects(response, redirect_to)
        self.assertContains(response, "This field is required.")
        reset_postlimit(bad_prof)

        # Legit comment
        response = self.client.post(url, {'post_id': post.id,
                                          'comment': 'some comment'},
                                    follow=True)
        redirect_to = '/blog/%s/post/%i/' % (user.username, post.id)
        self.assertRedirects(response, redirect_to)
        self.assertContains(response, "some comment")

        # Too fast
        response = self.client.post(url, {'post_id': post.id,
                                          'comment': 'AND ANOTHER THING'},
                                    follow=True)
        self.assertRedirects(response, redirect_to)
        self.assertContains(response, "Post rate limit exceeded<br />")

        # some scrub tries to post (user on probation)
        scrub_prof = Profile.objects.filter(probation=True).exclude(user__id=user.id)[0]
        scrub = scrub_prof.user
        reset_postlimit(scrub_prof)
        self.client.logout()
        self.client.login(username=scrub.username, password='password')
        response = self.client.post(url, {'post_id': post.id,
                                          'comment': "I'm a scrub, yo"},
                                    follow=True)
        self.assertRedirects(response, redirect_to)
        self.assertContains(response, "Thank you! Your comment will appear after a brief review.")
    
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
        url = '/blog/%s/new/' % user.username
        bad_user = User.objects.exclude(id=user.id)[0]
        
        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        
        response = self.client.post(url, {'title': "new title",
                                          'txt': "blah blah blah",
                                          'tags': "awesome post, great stuff"}, follow=True)
        self.assertEqual(response.status_code, 403)

        # other user logged in
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(url, {'title': "new title",
                                          'txt': "blah blah blah",
                                          'tags': "awesome post, great stuff"}, follow=True)
        self.assertEqual(response.status_code, 403)

        # blog author
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # invalid form
        response = self.client.post(url, {'title': "",
                                          'txt': "",
                                          'tags': ""}, follow=True)
        self.assertFormError(response, "form", 'title', "This field is required.")
        self.assertFormError(response, "form", 'txt', "This field is required.")

        # legit post
        response = self.client.post(url, {'title': "new title",
                                          'txt': "blah blah blah",
                                          'tags': "awesome post, great stuff"}, follow=True)
        self.assertEqual(response.status_code, 200)

    
    def test_edit_post(self):
        blog = Blog.objects.all()[0]
        user = blog.author
        post = blog.post_set.filter(draft=True)[0]
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/edit/%i/' % (user.username, post.id)

        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Wrong user
        self.client.logout()
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # legit request
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_show_drafts(self):
        user = Blog.objects.all()[0].author
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/blog/%s/drafts/' % user.username

        # not logged in
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
        url = '/blog/%s/save/' % user.username
        blog = Blog.objects.all()[0]
        user = blog.author
        bad_user = User.objects.exclude(id=user.id)[0]
        post = blog.post_set.filter(draft=True)[0]
        
        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # not logged in
        response = self.client.post(url, {'id': post.id,
                                          'txt': 'shady edit',
                                          'tags': "foo, bar, baz, bat",
                                          'title': 'shady title'})
        self.assertContains(response, "Unauthorized")
        
        # wrong user
        self.client.logout()
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'id': post.id,
                                          'txt': 'shady edit',
                                          'tags': "foo, bar, baz, bat",
                                          'title': 'shady title'})
        self.assertContains(response, "Unauthorized")
        
        # invalid form
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.post(url, {'id': post.id,
                                          'txt': '',
                                          'tags': "",
                                          'title': ''})
        self.assertContains(response, "Invalid Form")
        
        # legit save
        response = self.client.post(url, {'id': post.id,
                                          'txt': 'totally legit edit',
                                          'tags': "foo, bar, baz, bat",
                                          'title': 'totally legit title'})
        self.assertContains(response, "Draft Saved")

    
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
        
