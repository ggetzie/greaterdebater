from django.contrib.auth.models import User
from django.core import mail
from django.db.models import Max
from django.test import TestCase
from django.utils.html import escape

from comments.models import TopicComment, Debate, nVote, Draw, tcdMessage, \
    fcomMessage
from items.models import Topic, Tags
from profiles.models import Profile, Forgotten
from profiles.views import save_forgotten
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
        
        # User not logged in
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/?next=' + url)

        # Legit user
        self.client.login(username=tags.user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # List filtered by a tag
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
        
    def test_profile_msgs(self):
        
        user = User.objects.all()[0]
        url = '/users/messages/'
        
        # user not logged in
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/?next=' + url)
        
        # legit user 
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_message_detail(self):
        msg = tcdMessage.objects.all()[0]
        user = msg.recipient
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/users/u/' + user.username + '/messages/' + str(msg.id) + '/'
        
        # user not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # wrong user
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        # legit user 
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_replies(self):
        user = User.objects.all()[0]
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/users/replies/'

        # user not logged in
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/?next=' + url)
        
        # legit user 
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mark_read(self):
        url = '/users/mark_read/'
        fmsg = fcomMessage.objects.all()[0]
        user = fmsg.recipient
        bad_user = User.objects.exclude(id=user.id)[0]
        
        # GET request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")
        
        # bad user
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'id': fmsg.id})
        self.assertContains(response, "Not for you")
        self.client.logout()

        # legit user
        self.client.login(username=user.username, password='password')

        # bad id
        response = self.client.post(url, {'id': fmsg.id+99999999999})
        self.assertContains(response, "Message does not exist")

        # success
        response = self.client.post(url, {'id': fmsg.id})
        self.assertContains(response, "ok")
        fmsg = fcomMessage.objects.get(id=fmsg.id)
        self.assertEqual(fmsg.is_read, True)

    def test_check_messages(self):
        url = '/users/check_messages/'
        
        # user not logged in
        response = self.client.get(url)
        self.assertContains(response, "Not Logged In")
        
        user = User.objects.all()[0]
        self.client.login(username=user.username, password='password')

        # legit request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_stg(self):

        user = User.objects.all()[0]
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/users/settings/'

        # User not logged in
        self.client.logout()
        response = self.client.get(url)
        self.assertRedirects(response, '/users/login/?next=' + url)

        # Invalid Form
        self.client.login(username=user.username, password='password')
        response = self.client.post(url, {'email': ''})

        self.assertFormError(response, 'form', 'email', 'This field is required.')

        response = self.client.post(url, {'email': 'notanemail',
                                          'newwindows': False,
                                          'feedcoms': False,
                                          'feedtops': False,
                                          'feeddebs': False,
                                          'followcoms': False,
                                          'followtops': False})
        self.assertFormError(response, 'form', 'email', 'Enter a valid e-mail address.')

        # Legit
        response = self.client.post(url, {'email': 'changedemail@test.com',
                                          'newwindows': False,
                                          'feedcoms': False,
                                          'feedtops': False,
                                          'feeddebs': False,
                                          'followcoms': False,
                                          'followtops': False,
                                          'request_email': user.email})
        self.assertContains(response, 'Changes saved')

    def test_reset(self):
        user = User.objects.all()[0]
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/users/u/' + user.username + '/reset/'

        # user not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # wrong user
        self.client.login(username=bad_user.username, password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(url, {'new_password1':'nobananas',
                                          'new_password2':'nobananas'}, follow=True)
        self.assertEqual(response.status_code, 403)

        # correct user, GET
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        # Passwords don't match
        response = self.client.post(url, {'new_password1':'nobananas',
                                          'new_password2':'something else'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'New password fields must match.')
        
        # successful change
        response = self.client.post(url, {'new_password1':'nobananas',
                                          'new_password2':'nobananas'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password changed!')

        # forgotten password
        self.client.logout()
        code = save_forgotten(user)
        code_url = url + code 
        response = self.client.get(code_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'new_password1':'nobananas',
                                          'new_password2':'nobananas',
                                          'code':code}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password changed!')

        bad_code_url = url + ('b'* 32)
        response = self.client.get(bad_code_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_messages(self):
        user = User.objects.all()[0]
        bad_user = User.objects.exclude(id=user.id)[0]
        url = '/users/delete_messages/'

        msgs = []
        for i in range(10):
            m = tcdMessage(user=bad_user,
                                   recipient=user,
                                   comment="some message number " + str(i),
                                   subject="message " + str(i))
            m.save()
            msgs.append(m)

        message_list = ','.join([str(m.id) for m in msgs])
        
        # GET Request
        response = self.client.get(url)
        self.assertContains(response, "Not a POST")

        # No message list
        response = self.client.post(url, {'somecrap': 'andjunk'})
        self.assertContains(response, "No message list")

        # bad user
        self.client.login(username=bad_user.username, password='password')
        response = self.client.post(url, {'message_list': message_list})
        self.assertContains(response, "Messages could not be deleted")

        # legit user
        self.client.logout()
        self.client.login(username=user.username, password='password')
        response = self.client.post(url, {'message_list': message_list})
        self.assertContains(response, "Messages deleted")

    def test_delete_current_message(self):
        url = '/users/delete_current_message/'
        user = User.objects.all()[0]
        bad_user = User.objects.exclude(id=user.id)[0]

        
        for i in range(10):
            m = tcdMessage(user=bad_user,
                           recipient=user,
                           comment="some message number " + str(i),
                           subject="message " + str(i))
                           
            m.save()
            m.pub_date = datetime.datetime(year=2011,
                                           month=1,
                                           day=1,
                                           hour=1,
                                           minute=1,
                                           second=i)
            m.save()
        msgs = tcdMessage.objects.filter(recipient=user).order_by("pub_date")
        
        # User not logged in
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.client.login(username=bad_user.username, password='password')        

        # GET request
        response = self.client.get(url, follow=True)
        self.assertContains(response, "Not a POST")
        
        # No message id
        response = self.client.post(url, {"noid": "included"}, follow=True)
        self.assertContains(response, "No message id found")
        
        # No such message
        bad_id = tcdMessage.objects.aggregate(Max('id'))['id__max'] + 1
        response = self.client.post(url, {'message_id': bad_id}, follow=True)
        self.assertEqual(response.status_code, 404)
        
        # bad user
        response = self.client.post(url, {"message_id": msgs[4].id}, follow=True)
        self.assertEqual(response.status_code, 403)

        # legit delete
        self.client.logout()
        self.client.login(username=user.username, password='password')
        d_id = msgs[4].id
        deleted_date = msgs[4].pub_date
        redirect_id = msgs.filter(pub_date__gt=deleted_date)[0].id
        response = self.client.post(url, {"message_id": msgs[4].id}, follow=True)
        self.assertRedirects(response, 
                             '/users/u/' + user.username + '/messages/' + str(redirect_id))
        self.assertContains(response, "Message deleted")

        
    def test_feedback(self):
        url = '/users/feedback/'
        
        # GET request 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Anonyous user
        response = self.client.post(url, 
                                    {'subject': "Feedback subject",
                                     'message': "Hooray! Feedback!"},
                                    follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Feedback subject")
        self.assertNotEqual(mail.outbox[0].body.find("Anonymous user"), -1)
        self.assertEqual(response.status_code, 200)

        # Logged in user
        user = User.objects.all()[0]
        mail.outbox=[]
        self.client.login(username=user.username, password='password')
        response = self.client.post(url, 
                                    {'subject': "logged-in Feedback subject",
                                     'message': "Hooray! Feedback!"},
                                    follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "logged-in Feedback subject")
        self.assertNotEqual(mail.outbox[0].body.find(user.username), -1)
        self.assertNotEqual(mail.outbox[0].body.find(user.email), -1)
        self.assertEqual(response.status_code, 200)
        
        # Empty form
        response = self.client.post(url, 
                                    {'subject': "",
                                     'message': ""},
                                    follow=True)
        self.assertFormError(response, 'form', 'message', 'This field is required.')
        self.assertEqual(response.status_code, 200)

        # Form with no subject
        mail.outbox = []
        response = self.client.post(url, 
                                    {'subject': "",
                                     'message': "I don't need no stinking subject"},
                                    follow=True)
        self.assertEqual(mail.outbox[0].subject, 'GreaterDebater Feedback')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        user = User.objects.all()[0]
        url = '/users/forgot/'

        # GET Request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Empty Form
        response = self.client.post(url, {'email': ''}, follow=True)
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        self.assertEqual(response.status_code, 200)

        # Invalid email
        response = self.client.post(url, {'email': 'herpderp'}, follow=True)
        self.assertFormError(response, 'form', 'email', 'Enter a valid e-mail address.')
        self.assertEqual(response.status_code, 200)

        # Email not a user
        response = self.client.post(url, {'email': 'herp@derp.com'}, follow=True)
        self.assertFormError(response, 'form', None, 'email address not found')
        self.assertEqual(response.status_code, 200)

        # Legit request
        response = self.client.post(url, {'email': user.email}, follow=True)
        self.assertContains(response, 
                            "An email with instructions for resetting your password has been sent to the address you provided.")
        self.assertEqual(mail.outbox[0].subject, 'Reset your password at GreaterDebater')
        
