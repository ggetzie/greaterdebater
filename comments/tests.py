from django.test import TestCase

from items.models import Topic
from comments.models import TopicComment
from profiles.models import Profile

from testsetup import testsetup

import datetime

class ViewTest(TestCase):

    def setUp(self):
        testsetup()

    def confirm(self, response, msglist):
        for msg in msglist:
            self.assertContains(response, msg)

    def test_toggle_follow(self):
        top = Topic.objects.all().order_by('sub_date')[0]
        tcom = TopicComment.objects.filter(first=False,
                                           needs_review=False)[0]

        # user not logged in
        response = self.client.post('/comments/follow/',
                                    {'item': 'Topic',
                                     'id': top.id})
        self.confirm(response, ['<status>error</status>',
                                      'Not logged in'])

        # success Topic
        self.client.login(username='user2', password='password')
        response = self.client.post('/comments/follow/',
                                    {'item': 'Topic',
                                     'id': top.id})
        self.confirm(response, ['<status>ok</status>',
                                     'Topic followed'])
        
        # success TopicComment
        response = self.client.post('/comments/follow/',
                                    {'item': 'TopicComment',
                                     'id': tcom.id})
        self.confirm(response, ['<status>ok</status>',
                                     'TopicComment followed'])
        
        # Success unfollow Topic
        self.client.login(username='user1', password='password')
        top = Topic.objects.filter(followers__username='user1')[0]
        tcom = TopicComment.objects.filter(followers__username='user1')[0]

        response = self.client.post('/comments/follow/',
                                    {'item': 'Topic',
                                     'id': top.id})
        self.confirm(response, ['<status>ok</status>',
                                     'Topic no longer followed'])

        # Success unfollow TopicComment
        response = self.client.post('/comments/follow/',
                                    {'item': 'TopicComment',
                                     'id': tcom.id})
        self.confirm(response, ['<status>ok</status>',
                                     'TopicComment no longer followed'])
        
        # GET request
        response = self.client.get('/comments/follow/')
        self.confirm(response, ['<status>error</status>',
                                     'Not a POST'])

        # Invalid Form
        response = self.client.post('/comments/follow/',
                                    {'item': None,
                                     'id': None})
        self.confirm(response, ['<status>error</status>',
                                     'Invalid Form'])

        # Bad item id
        response = self.client.post('/comments/follow/',
                                    {'item': 'Topic',
                                     'id': 9999})
        self.confirm(response, ['<status>error</status>',
                                     'Item not found'])

        # Bad item type
        response = self.client.post('/comments/follow/',
                                    {'item': 'foo',
                                     'id': top.id})
        self.confirm(response, ['<status>error</status>',
                                     'No items of type foo'])

    def test_add(self):

        def reset_postlimit(prof):
            prof.rate = 0
            prof.last_post = datetime.datetime(month=1, day=1, year=1970)
            prof.save()

        top = Topic.objects.get(title="Topic 2")
        parent = TopicComment.objects.filter(ntopic=top,
                                             needs_review=False,
                                             first=False)[0]
        url = '/'.join(['', 'comments', str(top.id), 'add', ''])
        redirect1 = ''.join(['/users/login/?next=/', str(top.id), '/'])
        redirect2 = ''.join(['/', str(top.id), '/'])

        topcomment = {'comment': "test top comment",
                      'toplevel': 1}

        replycomment = {'comment': "test reply comment",
                        'toplevel': 0,
                        'parent_id': parent.id,
                        'nesting': parent.nnesting}

        # User not logged in
        response = self.client.post(url, {'comment': "test comment",
                                          'toplevel': 1})
        self.assertRedirects(response, redirect1)

        self.client.login(username='user1', password='password')
        prof = Profile.objects.get(user__username='user1')

        #  GET Request
        response = self.client.get(url)
        self.assertRedirects(response, redirect2)
        reset_postlimit(prof)

        # Valid comment, top level
        response = self.client.post(url, topcomment, follow=True)
        self.assertRedirects(response, redirect2)
        self.assertContains(response, "test top comment")
        reset_postlimit(prof)

        # Valid comment, reply
        response = self.client.post(url, replycomment, follow=True)
        self.assertRedirects(response, redirect2)
        self.assertContains(response, "test reply comment")


        # Submitting too fast
        response = self.client.post(url, {'comment': 'too fast',
                                          'toplevel': 1}, follow=True)
        self.assertRedirects(response, redirect2)
        self.assertContains(response, "rate limit exceeded")
        reset_postlimit(prof)
        
        # Invalid Form
        response = self.client.post(url, {'comment': '',
                                          'toplevel': 1}, follow=True)
        self.assertRedirects(response, redirect2)
        self.assertContains(response, "Oops! A problem occurred.")
        
