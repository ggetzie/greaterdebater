from django.contrib.auth.models import User
from django.test import TestCase

from comments.models import TopicComment
from items.models import Topic
from profiles.models import Profile
from testsetup import testsetup

class ViewTest(TestCase):

    def setUp(self):
        testsetup()
    
    def test_frontpage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_hot(self):
        response = self.client.get('/hot/')
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_submit_topic(self):
        # This should test POST request as well
        response = self.client.get('/submit/')
        self.assertEqual(response.status_code, 200)

    def test_comments(self):
        top = Topic.objects.filter(needs_review=False,
                                   spam=False)[0]
        response = self.client.get('/' + str(top.id) + '/')
        self.assertEqual(response.status_code, 200)

    def test_tflag(self):
        # This should be POST needs better testing
        # AJAX function - check response msg in XML
        response = self.client.get('/tflag/')
        self.assertEqual(response.status_code, 200)

    def test_delete_topic(self):
        # This should be POST needs better testing
        # AJAX function - check response msg in XML
        response = self.client.get('/topics/delete/')
        self.assertEqual(response.status_code, 200)

    def test_edit_topic(self):
        # This should test POST requests as well
        # also has to test that request comes from topic owner
        
        # topic owner GET request
        top = Topic.objects.filter(needs_review=False,
                                   spam=False)[0]
        self.client.login(username=top.user.username, password='password')
        response = self.client.get('/edit/' + str(top.id) + '/1/')
        self.assertEqual(response.status_code, 200)

    def test_review(self):
        # not logged in
        response = self.client.get('/review/topic/')
        self.assertContains(response, "Unauthorized", status_code=403)

        response = self.client.get('/review/comment/')
        self.assertContains(response, "Unauthorized", status_code=403)

        # non-staff user
        baduser = User.objects.filter(is_staff=False)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.get('/review/topic/')
        self.assertContains(response, "Unauthorized", status_code=403)

        response = self.client.get('/review/comment/')
        self.assertContains(response, "Unauthorized", status_code=403)

        # staff user
        gooduser = User.objects.filter(is_staff=True)[0]
        self.client.login(username=gooduser.username, password='password')
        response = self.client.get('/review/topic/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/review/comment/')
        self.assertEqual(response.status_code, 200)

    def test_decide(self):
        turl = '/decide/topic/'
        curl = '/decide/comment/'
        
        top = Topic.objects.filter(needs_review=True, spam=False)[0]
        com = TopicComment.objects.filter(needs_review=True, spam=False)[0]
        
        # user not logged in
        response = self.client.post(turl, {'id': top.id, 'decision': 0})
        self.assertContains(response, "Unauthorized")

        # non staff user
        baduser = User.objects.filter(is_staff=False)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.post(turl, {'id': top.id, 'decision': 0})
        self.assertContains(response, "Unauthorized")        

        # Valid user
        gooduser = User.objects.filter(is_staff=True)[0]
        self.client.login(username=gooduser.username, password='password')
        
        # Invalid Form
        response = self.client.post(turl, {'id': '', 'decision': ''})
        self.assertContains(response, "Invalid Form")

        # nonexistent topic
        response = self.client.post(turl, {'id': 9999, 'decision': 0})
        self.assertContains(response, "Object not found")

        # nonexistent comment
        response = self.client.post(curl, {'id': 9999, 'decision': 0})
        self.assertContains(response, "Object not found")

        # Topic that doesn't need review
        goodtop = Topic.objects.filter(needs_review=False)[0]
        response = self.client.post(turl, {'id': goodtop.id, 'decision': 0})
        self.assertContains(response, "Object not found")

        # Comment that doesn't need review
        goodcom = TopicComment.objects.filter(needs_review=False)[0]
        response = self.client.post(turl, {'id': goodcom.id, 'decision': 0})
        self.assertContains(response, "Object not found")

        # Approve Topic
        response = self.client.post(turl, {'id': top.id, 'decision': 0})
        self.assertContains(response, "topic approved")
        top = Topic.objects.get(id=top.id)
        self.assertEqual(top.needs_review, False)

        # Approve Comment
        response = self.client.post(curl, {'id': com.id, 'decision': 0})
        self.assertContains(response, "comment approved")
        com = TopicComment.objects.get(id=com.id)
        self.assertEqual(com.needs_review, False)

        top = Topic.objects.filter(needs_review=True, spam=False)[0]
        com = TopicComment.objects.filter(needs_review=True, spam=False)[0]

        # Disapprove Topic
        response = self.client.post(turl, {'id': top.id, 'decision': 1})
        self.assertContains(response, "topic marked as spam. User disabled")
        top = Topic.objects.get(id=top.id)
        self.assertEqual(top.spam, True)
        prof = Profile.objects.get(user=top.user)
        self.assertEqual(prof.rate, 10)

        # Disapprove Comment
        response = self.client.post(curl, {'id': com.id, 'decision': 1})
        self.assertContains(response, "comment marked as spam. User disabled")
        com = TopicComment.objects.get(id=com.id)
        self.assertEqual(com.spam, True)
        prof = Profile.objects.get(user=com.user)
        self.assertEqual(prof.rate, 10)
        

#     def test_addtags(self):
#         # This should test only POST requests
#         # AJAX function - check response msg in XML
#         response = self.client.get('/topics/addtags/')
#         self.assertEqual(response.status_code, 200)

#     def test_challenge(self):
#         # This should test post requests
#         response = self.client.get('/argue/challenge/1/')
#         self.assertEqual(response.status_code, 302)

    
