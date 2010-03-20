from django.test import TestCase

from items.models import Topic
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

#     def test_addtags(self):
#         # This should test only POST requests
#         # AJAX function - check response msg in XML
#         response = self.client.get('/topics/addtags/')
#         self.assertEqual(response.status_code, 200)

#     def test_challenge(self):
#         # This should test post requests
#         response = self.client.get('/argue/challenge/1/')
#         self.assertEqual(response.status_code, 302)

    
