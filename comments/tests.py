from django.test import TestCase
from django.contrib.auth.models import User

from items.models import Topic
from comments.models import TopicComment, Debate
from profiles.models import Profile

from testsetup import testsetup

import datetime

class ViewTest(TestCase):
    # fixtures = ['testdata.json']

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
                                '<message>on</message>'])
        
        # success TopicComment
        response = self.client.post('/comments/follow/',
                                    {'item': 'TopicComment',
                                     'id': tcom.id})
        self.confirm(response, ['<status>ok</status>',
                                '<message>on</message>'])
        
        # Success unfollow Topic
        self.client.login(username='user0', password='password')
        top = Topic.objects.filter(followers__username='user0')[0]
        tcom = TopicComment.objects.filter(followers__username='user0')[0]

        response = self.client.post('/comments/follow/',
                                    {'item': 'Topic',
                                     'id': top.id})
        self.confirm(response, ['<status>ok</status>',
                                '<message>off</message>'])

        # Success unfollow TopicComment
        response = self.client.post('/comments/follow/',
                                    {'item': 'TopicComment',
                                     'id': tcom.id})
        self.confirm(response, ['<status>ok</status>',
                                '<message>off</message>'])

        
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
        self.confirm(response, ['<status>alert</status>',
                                     'Item not found'])

        # Bad item type
        response = self.client.post('/comments/follow/',
                                    {'item': 'foo',
                                     'id': top.id})
        self.confirm(response, ['<status>alert</status>',
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
        url = '/comments/' + str(top.id) + '/add/'

        redirect1 = '/users/login/?next=/' + str(top.id) + '/'
        redirect2 = '/' + str(top.id) + '/'

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

        # User on probation
        prob = Profile.objects.filter(probation=True)[0]
        reset_postlimit(prob)
        self.client.login(username=prob.user.username, password='password')
        response = self.client.post(url, {'comment': "some kind of crap",
                                          'toplevel': 1}, follow=True)
        self.assertRedirects(response, redirect2)
        self.assertContains(response, "Thank you. Your comment will appear after a brief review.")
        self.assertNotContains(response, "some kind of crap")
        
    def test_edit(self):
        
        com = TopicComment.objects.filter(nparent_id=0, first=False, needs_review=False)[0]
        
        url = '/comments/' + str(com.ntopic.id) + '/edit/'
        redirect = '/' + str(com.ntopic.id) + '/'

        # User not logged in
        response = self.client.post(url, {'comment': 'test edit', })
        self.assertRedirects(response, redirect)
                                          
        # all test user passwords are 'password'
        self.client.login(username=com.user.username, password='password')
        
        # GET Request
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirect)
        self.assertContains(response, "Not a POST")

        # Invalid Form
        response = self.client.post(url, {'comment': '',
                               'parent_id': com.id}, follow=True)

        self.assertRedirects(response, redirect)
        self.assertContains(response, "<p>Oops! A problem occurred.</p>")
        

        # Valid Edit
        response = self.client.post(url, {'comment': 'test edit',
                                       'parent_id': com.id}, follow=True)
        self.assertRedirects(response, redirect)
        self.assertContains(response, "test edit")

        # Wrong user
        baduser = User.objects.exclude(id=com.user.id)[0]
        self.client.login(username=baduser.username, password='password')

        response = self.client.post(url, {'comment': 'test edit',
                                       'parent_id': com.id}, follow=True)
        self.assertRedirects(response, redirect)
        self.assertContains(response, "<p>Can't edit another user's comment!</p>")

    def test_delete(self):
        com = TopicComment.objects.filter(first=False, needs_review=False)[0]
        url = '/comments/delete/'

        # GET request        
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Wrong user
        baduser = User.objects.exclude(id=com.user.id)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.post(url, {'comment_id': com.id})
        self.assertContains(response, "delete a comment that isn")

        # Invalid Form
        self.client.login(username=com.user.username, password='password')
        response = self.client.post(url, {'comment_id': '',})
        self.assertContains(response, "Invalid Form")
        
        # Comment with debates associated
        response = self.client.post(url, {'comment_id': com.id})
        self.assertContains(response, "t delete a comment that has debates")

        # Valid delete
        coms = TopicComment.objects.filter(first=False, needs_review=False)
        # Find a comment without any debates
        for c in coms:
            if not c.debate_set.all():
                com2 = c
                break
                                          
        self.client.login(username=com2.user.username, password='password')
        response = self.client.post(url, {'comment_id': com2.id})
        self.assertContains(response, "<status>ok</status>")

        # Valid undelete
        com = TopicComment.objects.filter(first=False, needs_review=False, removed=True)[0]
        response = self.client.post(url, {'comment_id': com2.id})
        self.assertContains(response, "<status>ok</status>")

    def test_comment_detail(self):
        topcom = TopicComment.objects.filter(first=False, 
                                             needs_review=False, 
                                             spam=False,
                                             nparent_id=0)[0]

        childcom = TopicComment.objects.filter(first=False, 
                                             needs_review=False, 
                                             spam=False,
                                             nparent_id__gt=0)[0]

        parentcom = TopicComment.objects.get(id=childcom.nparent_id)
        
        topurl = '/comments/' + str(topcom.id) + '/'
        contexturl = '/comments/' + str(childcom.id) + '/?context=1'

        # Test without context
        response = self.client.get(topurl)
        self.assertContains(response, "You are viewing a single comment's thread")
        self.assertContains(response, topcom.comment_html)

        # Test with context
        response = self.client.get(contexturl)
        self.assertContains(response, "You are viewing a single comment's thread")
        self.assertContains(response, childcom.comment_html)
        self.assertContains(response, parentcom.comment_html)


        user = User.objects.all()[0]
        self.client.login(username=user.username, password='password')

        # Test without context logged in
        response = self.client.get(topurl)
        self.assertContains(response, "You are viewing a single comment's thread")
        self.assertContains(response, topcom.comment_html)

        # Test with context logged in
        response = self.client.get(contexturl)
        self.assertContains(response, "You are viewing a single comment's thread")
        self.assertContains(response, childcom.comment_html)
        self.assertContains(response, parentcom.comment_html)

    def test_arguments(self):
        deb = Debate.objects.filter(status__range=(1,5))[0]
        url = '/comments/' + str(deb.incite.id) + '/arguments/'

        response = self.client.get(url)
        self.assertContains(response, deb.title)
        self.assertContains(response, deb.incite.comment_html)
        
    def test_flag(self):
        url = '/comments/flag/'
        staffuser = User.objects.filter(is_staff=True)[0]
        reguser = User.objects.filter(is_staff=False)[0]
        com = TopicComment.objects.filter(needs_review=False,
                                          spam=False,
                                          first=False).exclude(user__id__in=[staffuser.id, reguser.id])[0]
        #User not logged in
        response = self.client.post(url, {'object_id': com.id})
        self.assertContains(response, "Not logged in")
        
        
        self.client.login(username=reguser.username, password='password')
        
        # Get request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")
        
        # invalid form
        response = self.client.post(url, {'object_id': ''})
        self.assertContains(response, "Invalid Form")

        # bad id
        response = self.client.post(url, {'object_id': 99999})
        self.assertContains(response, "Object not found")

        # valid flag from nonstaff user
        response = self.client.post(url, {'object_id': com.id})
        self.assertContains(response, "Comment flagged")

        checkcom = TopicComment.objects.get(id=com.id)
        self.assertTrue(reguser in checkcom.cflaggers.all())

        # valid flag from staff user
        self.client.login(username=staffuser.username, password='password')
        response = self.client.post(url, {'object_id': com.id})
        self.assertContains(response, "Comment flagged")

        checkcom = TopicComment.objects.get(id=com.id)
        self.assertTrue(staffuser in  checkcom.cflaggers.all())
                            
        prof = Profile.objects.get(user=checkcom.user)
        self.assertEqual(prof.rate, 10)
