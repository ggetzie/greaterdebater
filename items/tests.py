from django.db.models import Max
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.html import escape

from comments.models import TopicComment, Debate, nVote, Draw
from items.models import Topic, Tags
from items.forms import tcdTopicSubmitForm
from profiles.models import Profile
from testsetup import testsetup, create_user, create_topic, create_tcomment

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

        self.assertRedirects(response, '/')
        self.assertContains(response, "Your previous topic is still awaiting review. <br />" + \
                                "Please wait until it has been approved before submitting another topic.")
        

    def test_edit_topic(self):

        top = Topic.objects.filter(needs_review=False,
                                   spam=False)[0]
        url = '/edit/' + str(top.id) + '/1/'

        # GET request, user does not own the topic
        baduser = User.objects.exclude(id=top.user.id)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # POST request, use does not own the topic
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
        response = self.client.get('/review/topic/', follow=True)
        self.assertRedirects(response, '/users/login/?next=/review/topic/')

        response = self.client.get('/review/comment/', follow=True)
        self.assertRedirects(response, '/users/login/?next=/review/comment/')

        # non-staff user
        baduser = User.objects.filter(is_staff=False)[0]
        self.client.login(username=baduser.username, password='password')
        response = self.client.get('/review/topic/', follow=True)
        self.assertRedirects(response, '/users/login/?next=/review/topic/')

        response = self.client.get('/review/comment/', follow=True)
        self.assertRedirects(response, '/users/login/?next=/review/comment/')

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

        # Mark Topic as spam and disable user
        response = self.client.post(turl, {'id': top.id, 'decision': 1})
        self.assertContains(response, "topic marked as spam. User disabled")
        top = Topic.objects.get(id=top.id)
        self.assertEqual(top.spam, True)
        prof = Profile.objects.get(user=top.user)
        self.assertEqual(prof.rate, 10)

        # Mark Comment as spam and disable user
        response = self.client.post(curl, {'id': com.id, 'decision': 1})
        self.assertContains(response, "comment marked as spam. User disabled")
        com = TopicComment.objects.get(id=com.id)
        self.assertEqual(com.spam, True)
        prof = Profile.objects.get(user=com.user)
        self.assertEqual(prof.rate, 10)

        # Add a new topic needing review
        prof = Profile.objects.filter(probation=True, rate__lt=10)[0]
        
        top = create_topic(user=prof.user, title="Not quite spam", comment="test")
        top.save()
        com = create_tcomment(user=prof.user, top=top, txt="some crap")
        com.save()

        # Reject Topic
        response = self.client.post(turl, {'id': top.id, 'decision': 2})
        self.assertContains(response, "topic rejected")
        top = Topic.objects.get(id=top.id)
        self.assertEqual(top.spam, True)
        prof = Profile.objects.get(user=top.user)
        self.assertNotEqual(prof.rate, 10)

        # Reject Comment
        response = self.client.post(curl, {'id': com.id, 'decision': 2})
        self.assertContains(response, "comment rejected")
        com = TopicComment.objects.get(id=com.id)
        self.assertEqual(com.spam, True)
        prof = Profile.objects.get(user=com.user)
        self.assertNotEqual(prof.rate, 10)

        # When a user on probation makes a comment, don't alert followers
        # until after the comment is approved
        
        # create a topic with followers
        gu = Profile.objects.filter(probation=False, user__is_staff=False)[0].user
        ftopic = create_topic(gu, "Followed topic", "tag1", 
                              comment="Topic to test proper behavior of following")
        ftopic.followers.add(gu)
        
        # user on probation makes a comment
        self.client.logout()
        prof = Profile.objects.filter(probation=True)[0]
        bu = prof.user
        # reset rate limit
        prof.rate = 0
        prof.last_post = datetime.datetime(month=1, day=1, year=1970)
        prof.save()
        self.client.login(username=bu.username, password='password')
        response = self.client.post('/comments/'+ str(ftopic.id) +'/add/', 
                                    {'comment': 'probation follow test',
                                     'toplevel': 1}, 
                                    follow=True)
        self.assertRedirects(response, '/' + str(ftopic.id) + '/')

        # Follower checks replies, the above comment should not appear
        # because it still needs review
        self.client.logout()
        self.client.login(username=gu.username, password='password')
        response = self.client.get('/users/u/' + gu.username + '/replies/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'probation follow test')

        # Staff user approves comment
        self.client.logout()
        admin = User.objects.filter(is_staff=True)[0]
        self.client.login(username=admin.username, password='password')
        com = TopicComment.objects.filter(comment='probation follow test')[0]
        response = self.client.post(curl, {'id': com.id,
                                           'decision': 0})
        self.assertContains(response, "comment approved")
        
        # Now comment should appear when follower checks replies
        self.client.logout()
        self.client.login(username=gu.username, password='password')
        response = self.client.get('/users/u/' + gu.username + '/replies/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'probation follow test')
        

    def test_challenge(self):
        user = Profile.objects.filter(probation=False)[0].user
        c = TopicComment.objects.filter(first=False, 
                                        spam=False, 
                                        needs_review=False).exclude(user=user)[0]

        url = '/argue/challenge/' + str(c.id) + '/'
        postdata = {'title': "test debate", 
                    'argument': "just testing, bro"}
        
        # GET request
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Not a POST")

        # user not logged in
        response = self.client.post(url, postdata, follow=True)
        self.assertContains(response, "Please log in to start a debate")
        
        self.client.login(username=user.username, password="password")
        # invalid form
        response = self.client.post(url, {'title': '', 'argument': ''}, follow=True)
        self.assertContains(response, "Oops! A problem occurred.")

        # successful challenge
        response = self.client.post(url, postdata, follow=True)
        self.assertContains(response, "Challenged " + c.user.username + " to a debate")

        # Second challenge on same comment (not allowed)
        response = self.client.post(url, postdata, follow=True)
        self.assertContains(response, "You may only start one debate per comment")
        

    def test_vote(self):
        url = '/argue/vote/'
        deb = Debate.objects.filter(status__in=(1,2))[0]
        user = User.objects.exclude(username__in=(deb.plaintiff, deb.defendant))[0]
        postdata = {'argument': deb.id,
                    'voter': user.id,
                    'voted_for': 'P'}
        
        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")
        
        self.client.login(username = user.username, password='password')

        # Invalid form
        response = self.client.post(url, {'argument': '',
                                          'voter': '',
                                          'voted_for': ''})
        self.assertContains(response, "Invalid Form")

        # Vote from wrong user
        response = self.client.post(url, {'argument': deb.id,
                                          'voter': user.id-1,
                                          'voted_for': 'P'})
        self.assertContains(response, "Can't cast vote as another user")

        # legit vote
        response = self.client.post(url, postdata)
        self.assertContains(response, "ok")

    def test_unvote(self):
        url = '/argue/unvote/'
        
        # GET Request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        vote = nVote.objects.filter(argument__status__in=(1,2))[0]
        user = vote.voter
        self.client.login(username=user.username, password='password')
        
        # invalid form
        response = self.client.post(url, {'argument': '',
                                          'voter': ''})
        self.assertContains(response, 'Invalid Form')

        # wrong user id
        response = self.client.post(url, {'argument': vote.argument.id,
                                          'voter': user.id + 1})
        self.assertContains(response, "Can't delete another user's vote")

        # successful unvote
        response = self.client.post(url, {'argument': vote.argument.id,
                                          'voter': user.id})
        self.assertContains(response, "ok")

    def test_rebut(self):
        # Get active debate where it's the defendant's turn
        active_deb = Debate.objects.filter(status=2)[0]
        
        # Get inactive debate
        inactive_deb = Debate.objects.filter(status__gt=2)[0]
        

        url = '/argue/rebut/'

        # GET Request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")
        
        # Invalid Form
        user = active_deb.whos_up()
        bad_user = User.objects.exclude(id=user.id)[0]

        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'arg_id': '',
                                          'comment': ''})

        self.assertContains(response, "Invalid Form")

        # wrong user
        response = self.client.post(url, {'arg_id': active_deb.id,
                                          'comment': 'some rebuttal'})
        self.assertContains(response, "Not your turn")

        # legit rebuttal
        self.client.login(username=user.username, password='password')
        response = self.client.post(url, {'arg_id': active_deb.id,
                                          'comment': 'some rebuttal'})
        self.assertContains(response, "ok")

        # old argument
        old_user = inactive_deb.plaintiff
        self.client.login(username=old_user.username, password='password')
        response = self.client.post(url, {'arg_id': inactive_deb.id,
                                          'comment': 'some rebuttal'})
        self.assertContains(response, "Not your turn")

    def test_respond(self):
        url = '/argue/respond/'
        deb = Debate.objects.filter(status=0)[0]
        good_user = deb.defendant
        bad_user = User.objects.exclude(id=good_user.id)[0]
        postdata = {'arg_id': deb.id,
                    'user_id': good_user.id,
                    'response': 0}

        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Invalid form
        response = self.client.post(url, {'arg_id':'',
                                          'user_id':'',
                                          'response':''})
        self.assertContains(response, "Invalid Form")

        # Wrong user
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': bad_user.id,
                                          'response': 0})
        self.assertContains(response, escape("Can't respond to a challenge that's not for you!"))
        
        # Legit response
        self.client.login(username=good_user.username, password='password')
        response = self.client.post(url, postdata)
        self.assertContains(response, 'Challenge accepted')
        

        # Response already received
        adeb = Debate.objects.exclude(status=0)[0]
        self.client.login(username=adeb.defendant.username, password='password')
        response = self.client.post(url, {'arg_id': adeb.id,
                                          'user_id': adeb.defendant.id,
                                          'response': 0})

        
    def test_draw(self):
        url = '/argue/draw/'
        deb = Debate.objects.filter(status__in=(1,2))[0]
        
        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Invalid form
        response = self.client.post(url, {'arg_id':'',
                                          'user_id':'',
                                          'comment': ''})
        self.assertContains(response, "Invalid Form")
        
        # User offering a draw out of turn
        bad_user = deb.whos_up(invert=1)
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': bad_user.id,
                                          'comment': 'A draw I say'})
        self.assertContains(response, "Not your turn")

        # Legit draw
        good_user = deb.whos_up()
        self.client.login(username=good_user.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': good_user.id,
                                          'comment': 'A draw I say'})
        self.assertContains(response, "A draw I say")
        
        # Draw offer outstanding
        # opponent tries to offer a draw before responding
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': good_user.id,
                                          'comment': 'A draw I say'})
        self.assertContains(response, "A draw has already been offered")

    def test_respond_draw(self):
        url = '/argue/draw/respond/'
        drawoffer = Draw.objects.all()[0]
        deb = drawoffer.argument
        
        bu = User.objects.exclude(id = drawoffer.recipient.id)[0]
        gu = drawoffer.recipient

        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # invalid form
        response = self.client.post(url, {'arg_id': '',
                                          'user_id': '',
                                          'response': ''})
        self.assertContains(response, "Invalid Form")
        
        # bad user
        self.client.login(username=bu.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': bu.id,
                                          'response': 0})
        self.assertContains(response, escape("You can't respond to this draw offer"))
        
        # legit resposne
        self.client.login(username=gu.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': gu.id,
                                          'response': 0})
        self.assertContains(response, "Draw Accepted")

    def test_concede(self):
        url = '/argue/concede/'
        
        deb = Debate.objects.filter(status__in=(1,2))[0]
        gu = deb.whos_up()
        bu = User.objects.exclude(id=gu.id)[0]

        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # Invalid form
        response = self.client.post(url, {'arg_id': '',
                                          'user_id': ''})
        self.assertContains(response, "Invalid Form")

        # wrong user
        self.client.login(username=bu.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': bu.id})
        self.assertContains(response, "Not your turn")

        # legit concession
        self.client.login(username=gu.username, password='password')
        response = self.client.post(url, {'arg_id': deb.id,
                                          'user_id': gu.id})
        self.assertContains(response, "Point conceded")
        
    def test_arg_detail(self):
        
        debs = Debate.objects.all()
        
        # Debate status 0
        deb0 = debs.filter(status=0)[0]
        deb0url = '/argue/' + str(deb0.id) + '/'
        response = self.client.get(deb0url)
        self.assertEqual(response.status_code, 200)
        
        user = deb0.whos_up()
        self.client.login(username=user.username, password='password')
        response = self.client.get(deb0url)
        self.assertContains(response, "Begin this debate?")

        # Debate status 1
        deb1 = debs.filter(status=1)[0]
        deb1url = '/argue/' + str(deb1.id) + '/'
        self.client.logout()
        response = self.client.get(deb1url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "to cast your vote for the greater debater!")
        
        user = deb1.whos_up()
        self.client.login(username=user.username, password='password')
        response = self.client.get(deb1url)
        self.assertContains(response, "Concede argument: Are you sure?")

        user = deb1.whos_up(invert=1)
        self.client.login(username=user.username, password='password')
        response = self.client.get(deb1url)
        self.assertNotContains(response, "Concede argument: Are you sure?")

        user = User.objects.exclude(id__in=(deb1.plaintiff.id, deb1.defendant.id))[0]
        self.client.login(username=user.username, password='password')
        response = self.client.get(deb1url)
        self.assertNotContains(response, "Current Tally:")
        
        # Debate status 2
        deb2 = debs.filter(status=2)[0]
        response = self.client.get('/argue/' + str(deb2.id) + '/')
        self.assertEqual(response.status_code, 200)

        # Debate status 3
        deb3 = debs.filter(status=3)[0]
        deb3url = '/argue/' + str(deb3.id) + '/'
        response = self.client.get(deb3url)
        self.assertEqual(response.status_code, 200)

        user = deb3.plaintiff
        self.client.login(username=user.username, password='password')
        response = self.client.get(deb3url)
        self.assertContains(response, "Final Tally:")

        # Debate status 4
        deb4 = debs.filter(status=4)[0]
        response = self.client.get('/argue/' + str(deb4.id) + '/')
        self.assertEqual(response.status_code, 200)

        # Debate status 5
        deb5 = debs.filter(status=5)[0]
        response = self.client.get('/argue/' + str(deb5.id) + '/')
        self.assertEqual(response.status_code, 200)

        # Debate with outstanding draw offer
        drawoffer = Draw.objects.all()[0]
        debdo = drawoffer.argument
        debdourl = '/argue/' + str(debdo.id) + '/'
        response = self.client.get(debdourl)
        self.assertEqual(response.status_code, 200)

        user = debdo.whos_up()
        self.client.login(username=user.username, password='password')
        response = self.client.get(debdourl)
        self.assertContains(response, "Accept")

    def test_args_list(self):

        response = self.client.get('/argue/hot/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/argue/new/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/argue/archive/')
        self.assertEqual(response.status_code, 200)
