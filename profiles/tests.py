from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from comments.models import TopicComment, Debate, nVote, Draw
from items.models import Topic, Tags
from profiles.models import Profile, Forgotten
from testsetup import testsetup, create_user, create_topic, create_tcomment

import datetime

def test_get(testobj, url, user, other_user):
    # not logged in
    response = testobj.client.get(url)
    testobj.assertEqual(response.status_code, 200)

    # non-owner user
    testobj.client.login(username=other_user.username, password='password')
    response = testobj.client.get(url)
    testobj.assertEqual(response.status_code, 200)
    testobj.client.logout()

    # owner user
    testobj.client.login(username=user.username, password='password')
    response = testobj.client.get(url)
    testobj.assertEqual(response.status_code, 200)

class ViewTest(TestCase):
    
    def setUp(self):
        testsetup()

    def test_register(self):

        url = '/users/register/'

        # GET Request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Invalid Form
        response = self.client.post(url, {'username': '',
                                          'password1': '',
                                          'password2': '',
                                          'email': '',
                                          'next': '/'})
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password1", "This field is required.")        
        self.assertFormError(response, "form", "password2", "This field is required.")
        self.assertFormError(response, "form", "email", "This field is required.")

        response = self.client.post(url, {'username': 'newuser',
                                          'password1': 'passwords',
                                          'password2': 'dontmatch',
                                          'email': 'newuser@test.com',
                                          'next': '/'})
        self.assertFormError(response, "form", None, "Password fields must match")

        response = self.client.post(url, {'username': 'newuser#',
                                          'password1': 'password',
                                          'password2': 'password',
                                          'email': 'newuser@test.com',
                                          'next': '/'})
        self.assertFormError(response, "form", 'username', "Only letters and numbers allowed in username")

        bad_email = User.objects.all()[0].email
        response = self.client.post(url, {'username': 'newuser',
                                          'password1': 'password',
                                          'password2': 'password',
                                          'email': bad_email,
                                          'next': '/'})
        self.assertFormError(response, "form", 'email', "A user with that email address already exists")


        # success
        response = self.client.post(url, {'username': 'newuser',
                                          'password1': 'password',
                                          'password2': 'password',
                                          'email': 'newuser@test.com',
                                          'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertContains(response, "Welcome")

    def test_login(self):
        
        url = '/users/login/'
        
        # Get request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Invalid Form
        response = self.client.post(url, {'email': '',
                                          'password': ''})

        self.assertFormError(response, 'form', 'email', "This field is required.")
        self.assertFormError(response, 'form', 'password', "This field is required.")

        # Non existent user
        response = self.client.post(url, {'email': 'Inotreal@test.com',
                                          'password': 'bananas'})
        self.assertContains(response, escape("Sorry, that's not a valid username or password"))

        # Wrong password
        user = User.objects.all()[0]
        response = self.client.post(url, {'email': user.email,
                                          'password': 'bananas'})
        self.assertContains(response, escape("Sorry, that's not a valid username or password"))

        # Legit login
        response = self.client.post(url, {'email': user.email,
                                          'password': 'password',
                                          'next': '/'}, follow=True)
        self.assertRedirects(response, '/')
        self.assertContains(response, "Welcome")
        
        
    def test_profile(self):
        user = User.objects.all()[0]
        url = '/users/u/' + user.username + '/profile/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Settings")
        
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Settings")

    def test_profile_topics(self):
        user = User.objects.all()[0]
        url = '/users/u/' + user.username + '/submissions/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "delete")

        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "delete")

    def test_profile_saved(self):
    
        tags = Tags.objects.all()[0]
        url = '/users/u/' + tags.user.username + '/saved/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username=tags.user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        sometag = tags.tags.split(',')[0]
        url += sometag + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tagedit(self):
        tagobj = Tags.objects.all()[0]
        user = tagobj.user
        top = tagobj.topic
        
        url = '/users/u/' + user.username + '/tagedit/' + str(top.id) + '/'
        
        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # wrong user
        baduser = User.objects.exclude(id=user.id)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        
        # valid user
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_profile_args(self):
        user = User.objects.all()[0]
        url = '/users/u/' + user.username + '/arguments/'
        other_user = User.objects.exclude(id=user.id)[0]

        test_get(self, url, user, other_user)

    def test_profile_all_args(self):

        user = Debate.objects.all()[0].plaintiff
        other_user = User.objects.exclude(id=user.id)[0]
        pend_url = '/users/u/' + user.username + '/arguments/pending/'
        curr_url = '/users/u/' + user.username + '/arguments/current/'
        arch_url = '/users/u/' + user.username + '/arguments/complete/'
        
        test_get(self, pend_url, user, other_user)
        test_get(self, curr_url, user, other_user)
        test_get(self, arch_url, user, other_user)
        
        
