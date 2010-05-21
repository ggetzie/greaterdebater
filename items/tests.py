from django.db.models import Max
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from comments.models import TopicComment
from items.models import Topic, Tags
from items.forms import tcdTopicSubmitForm
from profiles.models import Profile
from testsetup import testsetup, create_user

import datetime

def topic_with_comments(tops, with_comments=True):
    """find a topic with or without comments, 
    excluding first comments, comments needing review,
    comments marked as spam, and comments that are removed"""
    for top in tops:
        coms = top.topiccomment_set.filter(first=False, removed=False,
                                           needs_review=False, spam=False)
        if not (with_comments ^ bool(coms)):
            return top

    return None

class ViewTest(TestCase):

    def setUp(self):
        testsetup()

    def test_comments(self):
        top = Topic.objects.filter(needs_review=False,
                                   spam=False)[0]
        # not logged in
        response = self.client.get('/' + str(top.id) + '/')
        self.assertEqual(response.status_code, 200)

        # logged in, not submitter
        user = User.objects.exclude(id=top.user.id)[0]
        self.client.login(username=user.username,
                          password='password')
        response = self.client.get('/' + str(top.id) + '/')
        self.assertEqual(response.status_code, 200)

        # logged in, submitter
        self.client.login(username=top.user.username,
                          password='password')
        response = self.client.get('/' + str(top.id) + '/')
        self.assertEqual(response.status_code, 200)

    def test_topics(self):
        url = '/hot/'
        
        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # logged in
        user = User.objects.all()[0]
        self.client.login(username=user.username, password="password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = '/new/'
        
        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # logged in
        user = User.objects.all()[0]
        self.client.login(username=user.username, password="password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_frontpage(self):
        url = '/'
        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # logged in
        user = User.objects.all()[0]
        self.client.login(username=user.username, password="password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tflag(self):
        url = '/tflag/'
        staffuser = User.objects.filter(is_staff=True)[0]
        reguser = User.objects.filter(is_staff=False)[0]
        top = Topic.objects.filter(needs_review=False,
                                   spam=False).exclude(user__in=[staffuser, reguser])[0]

        # Not logged in
        response = self.client.post(url, {'object_id':top.id})
        self.assertContains(response, "Not logged in")

        self.client.login(username=reguser.username, password='password')

        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Invalid form
        response = self.client.post(url, {'object_id':''})
        self.assertContains(response, "Invalid Form")

        # Nonexistent topic
        response = self.client.post(url, {'object_id':99999})
        self.assertContains(response, "Topic not found")

        # Valid regular user flag
        response = self.client.post(url, {'object_id':top.id})
        self.assertContains(response, "Topic flagged")
        checktop = Topic.objects.get(id=top.id)
        self.assertTrue(reguser in top.tflaggers.all())

        # Valid staff user flag
        self.client.login(username=staffuser.username, password='password')
        response = self.client.post(url, {'object_id':top.id})
        self.assertContains(response, "Topic flagged")
        checktop = Topic.objects.get(id=top.id)
        self.assertTrue(staffuser in top.tflaggers.all())
        prof = Profile.objects.get(user=top.user)
        self.assertEqual(prof.rate, 10)

    def test_delete_topic(self):
        url = '/topics/delete/'
        
        # GET Request
        response = self.client.get('/topics/delete/')
        self.assertContains(response, "Not a POST")
        
        # Nonexistent topic
        badid = Topic.objects.aggregate(Max('id'))['id__max'] + 1
        response = self.client.post(url, {'topic_id': badid})
        self.assertContains(response, "Topic not found")

        # POST without topic id
        response = self.client.post(url, {'wrongfield': badid})
        self.assertContains(response, "Invalid Form")

        # User does not own topic
        top = Topic.objects.all()[0]
        user = User.objects.exclude(id=top.user.id)[0]
        self.client.login(username=user.username, password="password")
        response = self.client.post(url, {'topic_id': top.id})
        self.assertContains(response, escape("Can't delete a topic that isn't yours"))
        
        # Valid user, but topic already has comments
        top = topic_with_comments(Topic.objects.all())
        self.client.login(username=top.user.username, password="password")
        response = self.client.post(url, {'topic_id': top.id})
        self.assertContains(response, escape("Can't delete a topic that has comments"))

        # Valid user, topic has no comments, successful delete
        top = topic_with_comments(Topic.objects.all(), with_comments=False)
        self.client.login(username=top.user.username, password="password")
        response = self.client.post(url, {'topic_id': top.id})
        self.assertContains(response, "Topic deleted. FOREVER.")

    def test_submit(self):
        url = '/submit/'
        # User not logged in
        response = self.client.get(url)
        self.assertContains(response, "Please log in or create an account to continue submitting your topic")

        prof = Profile.objects.filter(probation=False)[0]
        user = prof.user
        prof.last_post = datetime.datetime(month=1, day=1, year=1970)
        prof.save()
        self.client.login(username=user.username, password="password")

        # Invalid Form
        response = self.client.post(url, {'title': "",
                                          'url': "",
                                          'comment': "",
                                          'tags': ""})
        self.assertFormError(response, "form", "title", "This field is required.")


        # Valid submission
        redirect = '/%d/' % (Topic.objects.aggregate(Max('id'))['id__max'] + 1)
        response = self.client.post(url, {'title': "Test Topic",
                                          'url': "",
                                          'comment': "A topic for testing",
                                          'tags': "test"}, follow=True)

        self.assertRedirects(response, redirect)
        self.assertContains(response, "Test Topic")

        # Submitting too fast
        response = self.client.post(url, {'title': "Test Topic",
                                          'url': "",
                                          'comment': "A topic for testing",
                                          'tags': "test"}, follow=True)
        self.assertContains(response, "Post rate limit exceeded")

        # User on probation
        newuser, newprof = create_user(username="dodgeyuser", 
                                       password="password",
                                       email="dodgey@dodgey.com")

        self.client.login(username=newuser.username, password="password")
        response = self.client.post(url, {'title': "Dodgey Test Topic",
                                          'url': "",
                                          'comment': "A topic for testing",
                                          'tags': "test"}, follow=True)
        
        
        self.assertRedirects(response, '/')
        self.assertContains(response, "Thank you! Your topic will appear after a brief review.")

        # User on probation second submission
        newprof.last_post = datetime.datetime(month=1, day=1, year=1970)
        newprof.save()
        response = self.client.post(url, {'title': "Another dodgey Test Topic",
                                          'url': "",
                                          'comment': "A second topic for testing",
                                          'tags': "test"}, follow=True)
        print response
        self.assertRedirects(response, '/')
        self.assertContains(response, "Your previous topic is still awaiting review. <br />" + \
                                "Please wait until it has been approved before submitting another topic.")
        

    def test_edit_topic(self):
        # This should test POST requests as well
        # also has to test that request comes from topic owner
        

        top = Topic.objects.filter(needs_review=False,
                                   spam=False)[0]
        url = '/edit/' + str(top.id) + '/1/'

        # GET request, user does not own the topic
        baduser = User.objects.exclude(id=top.user.id)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # POST reques, use does not own the topic
        response = self.client.post(url, {'title': 'bad title',
                                          'comment' : 'bad comment'})
        self.assertEqual(response.status_code, 403)

        # GET request topic owner
        self.client.login(username=top.user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # POST request, invalid form
        response = self.client.post(url, {'title': '',
                                          'comment': 'edited comment'}, 
                                    follow=True)
        self.assertFormError(response, 'form', 'title', 'This field is required.')

        redirect = '/users/u/' + top.user.username + '/submissions/1'

        # POST request, valid
        response = self.client.post(url, {'title': 'edited title',
                                          'comment': 'edited comment'},
                                    follow=True)
        self.assertRedirects(response, redirect)
        self.assertContains(response, "edited title")

    def test_addtags(self):
        url = '/topics/addtags/'
        top = Topic.objects.all()[0]
        tags = {'source': 0,
                'topic_id': top.id}
        # user not logged in
        tags['tags'] = 'test tag'
        response = self.client.post(url, tags)
        self.assertContains(response, "Not logged in")

        user = Profile.objects.filter(probation=False, rate=0)[0].user
        self.client.login(username=user.username, password='password')

        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Empty form
        tags['tags'] = ''
        response = self.client.post(url, tags)
        self.assertContains(response, "This field is required")

        # Invalid character in tag field
        tags['tags'] = '<bad>'
        response = self.client.post(url, tags)
        self.assertContains(response, 
                            escape("Only letters, numbers, spaces and characters _ ! @ ? $ % # ' & are allowed in tags"))

        # Valid tag
        tags['tags'] = 'test tag'
        response = self.client.post(url, tags)
        self.assertContains(response, 'test tag')

    def test_remove_tag(self):
        url = '/topics/removetag/'
        tags = Tags.objects.all()[0]
        tag = tags.display_tags()[0]
        baduser = User.objects.exclude(id=tags.user.id)[0]
        postdata = {'user_id': tags.user.id,
                    'topic_id': tags.topic.id,
                    'tag': tag}

        # user not logged in
        response = self.client.post(url, postdata)
        self.assertContains(response, "Not logged in")

        # GET Request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")
        
        # Wrong user
        self.client.login(username=baduser.username, password='password')
        response = self.client.post(url, postdata)
        self.assertContains(response, escape("Can't remove another user's tag"))

        # Invalid Form
        self.client.login(username=tags.user.username, password='password')
        response = self.client.post(url, {'topic_id': '',
                                          'user_id': '',
                                          'tag': tag})
        self.assertContains(response, "Invalid Form")

        # Valid but nonexistent topic_id
        bad_id = Topic.objects.aggregate(Max('id'))['id__max'] + 1
        response = self.client.post(url, {'topic_id': bad_id,
                                          'user_id': tags.user.id,
                                          'tag': tag})
        self.assertContains(response, escape("Invalid topic, user or tag"))

        # Valid removal
        response = self.client.post(url, postdata)
        self.assertContains(response, "Tag removed")

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
