from django.contrib.auth.models import User

from blog.models import *
from comments.models import *
from items.models import *
from profiles.models import *
from utils import update_tags

from settings import HOSTNAME

import random
import string


TAGSCHAR = string.ascii_letters + "'_@?$%#& "
TLDS = ['.com', '.net', '.org', '.gov']

def random_words(chars, wordlen, numwords):
    # produce a list of numwords random words
    # each word is up to wordlen long and contains
    # allowed characters from chars
    return [''.join([random.choice(chars) for x in range(random.randint(1,wordlen))])
            for y in range(random.randint(1,numwords))]

def testsetup():
    # Create some users
    users = []
    profiles = []
    for i in range(20):
        username="user"+str(i)
        u, p = create_user(username=username, password="password",
                           email=username+"@test.com")
        
        if i == 0: # First users is superuser
            u.superuser = True
        if i < 5: # First 5 users are staff
            u.is_staff = True
        if not (i > 4 and i < 10): # users 5-9 are on probation
            p.probation = False
        if i > 9 and i < 15: # users 10-14 are shadowbanned
            p.shadowban = True
        users.append(u)
        profiles.append(p)
        u.save()
        p.save()

    good_users = [p.user for p in profiles if (not p.shadowban) and (not p.probation)]
    spam_users = [p.user for p in profiles if p.shadowban]
    prob_users = [p.user for p in profiles if p.probation]

    def add_followers(item, potential_followers):
        if random.random() < 0.75: # 75% chance of having any followers
            for i in range(random.randint(1,10)):
                # choose a random follower from the list of good users without replacement
                follower = potential_followers.pop(random.choice(range(len(potential_followers))))
                item.followers.add(follower)

    # Create 1 - 5 topics per user
    topics = []
    for u in users:
        for i in range(random.randint(1,5)):
            title = ' '.join(random_words(string.letters+string.punctuation, 15, 8))
            if random.random() > 0.25:
                tags = ','.join(random_words(TAGSCHAR, 15, 15))
                    
            else:
                tags = ''
                
            if random.random() > 0.25:
                comment = ' '.join(random_words(string.ascii_letters, 20, 500))
            else:
                comment = ''

            if random.random() > 0.1:
                url = ''.join(['http://', 
                              random_words(string.ascii_letters, 25, 1)[0], 
                              random.choice(TLDS)])
            else:
                url = ''
            
            top = create_topic(u, title, tags=tags, comment=comment, url=url)
            top.save()
            topics.append(top)

            add_followers(top, good_users[:])

            


    comments = []
    
    for top in topics:
        potential_parents = [None]
        if top.id % 3 == 0: continue # 1/3 of topics have no comments
        for i in range(random.randint(1,10)):
            if i == 3:
                user = random.choice(spam_users)
            elif i == 4:
                user = random.choice(prob_users)
            else:
                user = random.choice(good_users)
            parent = random.choice(potential_parents)
            new_tcom = create_tcomment(user, 
                                       top, 
                                       txt=' '.join(random_words(string.ascii_letters, 20, 1000)),
                                       parent=parent)
            
            # add  another None to keep the chance
            # of a new tcom being toplevel at 50%
            potential_parents += [new_tcom, None]
            comments += [new_tcom]
            add_followers(new_tcom, good_users[:])
            new_tcom.save()

            # alert follower of the parent comment (or the topic if it is top level) 
            # that a new reply has been made
            if parent: 
                followers=parent.followers.all()
            else: 
                followers=top.followers.all()
                
            for foll in followers:
                fmsg = fcomMessage(recipient=foll,
                                   is_read=False,
                                   reply=new_tcom,
                                   pub_date=datetime.datetime.now())
                fmsg.save()



    ##  Create some debates
    good_comments = [c for c in comments if not (c.spam or c.needs_review)]
    com1 = comments[1]
    debaters = [u for u in good_users if not u == com1.user]
    # Pending debate, status=0
    deb_pending = Debate(plaintiff=debaters[1],
                         defendant=com1.user,
                         status=0,
                         incite=com1,
                         title="Pending Debate",
                         start_date=datetime.datetime.now(),
                         topic=com1.ntopic)
    deb_pending.save()

    deb_alert = tcdMessage(recipient=deb_pending.defendant,
                           comment = "You have been challenged to a Debate",
                           subject="Challenge!",
                           pub_date=datetime.datetime.now(), 
                           user=deb_pending.plaintiff)
    deb_alert.save()

    deb_pending_com1 = ArgComment(user=deb_pending.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pending,
                                  pub_date=datetime.datetime.now(),
                                  comment="Pending debate challenge")
    deb_pending_com1.save()

    # Debate, plaintiff's turn status=1
    deb_pturn = Debate(plaintiff=debaters[2],
                       defendant=com1.user,
                       status=1,
                       incite=com1,
                       title="Debate - Plaintiff turn",
                       start_date=datetime.datetime.now(),
                       topic=com1.ntopic)
    deb_pturn.save()
    deb_pturn_com1 = ArgComment(user=deb_pturn.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pturn,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plantiff turn challenge")
    deb_pturn_com1.save()

    deb_pturn_com2 = ArgComment(user=deb_pturn.defendant,
                                  ntopic=com1.ntopic,
                                  debate=deb_pturn,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plantiff turn 1st rebuttal")
    deb_pturn_com2.save()

    # Debate, plaintiff's turn status = 1
    # with outstanding draw offer
    deb_drawoffer = Debate(plaintiff=debaters[6],
                           defendant = com1.user,
                           status=1,
                           incite=com1,
                           title = "Debate - Draw offered",
                           start_date=datetime.datetime.now(),
                           topic=com1.ntopic)
    deb_drawoffer.save()
    deb_drawoffer_com1 = ArgComment(user=deb_drawoffer.plaintiff,
                                    ntopic=com1.ntopic,
                                    debate=deb_drawoffer,
                                    pub_date=datetime.datetime.now(),
                                    comment="Draw offer challenge")
    deb_drawoffer_com1.save()

    deb_drawoffer_com2 = ArgComment(user=deb_drawoffer.defendant,
                                    ntopic=com1.ntopic,
                                    debate=deb_drawoffer,
                                    pub_date=datetime.datetime.now(),
                                    comment="Explaining why for draw")
    deb_drawoffer_com2.save()
    
    drawoffer = Draw(offeror = deb_drawoffer.defendant,
                     recipient = deb_drawoffer.plaintiff,
                     offer_date = datetime.datetime.now(),
                     argument = deb_drawoffer)
    
    drawoffer.save()

    # Debate, defendant's turn status=2
    deb_dturn = Debate(plaintiff=debaters[3],
                       defendant=com1.user,
                       status=2,
                       incite=com1,
                       title="Debate - Defendent turn",
                       start_date=datetime.datetime.now(),
                       topic=com1.ntopic)
    deb_dturn.save()
    deb_dturn_com1 = ArgComment(user=deb_dturn.plaintiff,
                                ntopic=com1.ntopic,
                                debate=deb_dturn,
                                pub_date=datetime.datetime.now(),
                                comment="Defendant turn challenge")
    deb_dturn_com1.save()

    # Some votes for this debate
    voters = [u for u in debaters if not (u == deb_dturn.plaintiff or 
                                          u == deb_dturn.defendant)]
    vote1 = nVote(argument=deb_dturn,
                  voter=voters[0],
                  voted_for="P")
    vote1.save()

    vote2 = nVote(argument=deb_dturn,
                  voter=voters[1],
                  voted_for="D")
    vote2.save()
    

    # Debate, defendant wins, status = 3
    deb_dwin = Debate(plaintiff=debaters[4],
                      defendant=com1.user,
                      status=3,
                      incite=com1,
                      title="Debate - Defendent wins",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_dwin.save()
    deb_dwin_com1 = ArgComment(user=deb_dwin.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_dwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Defendant win challenge")
    deb_dwin_com1.save()

    deb_dwin_com2 = ArgComment(user=deb_dwin.defendant,
                                  ntopic=com1.ntopic,
                                  debate=deb_dwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Defendant win 1st rebuttal")
    deb_dwin_com2.save()

    # Debate, plaintiff wins, status = 4
    deb_pwin = Debate(plaintiff=debaters[5],
                      defendant=com1.user,
                      status=4,
                      incite=com1,
                      title="Debate - Plaintiff wins",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_pwin.save()
    deb_pwin_com1 = ArgComment(user=deb_pwin.plaintiff,
                               ntopic=com1.ntopic,
                               debate=deb_pwin,
                               pub_date=datetime.datetime.now(),
                               comment="Plaintiff win challenge")
    deb_pwin_com1.save()

    deb_pwin_com2 = ArgComment(user=deb_pwin.defendant,
                               ntopic=com1.ntopic,
                               debate=deb_pwin,
                               pub_date=datetime.datetime.now(),
                               comment="Plaintiff win 1st rebuttal")
    deb_pwin_com2.save()

    deb_pwin_com3 = ArgComment(user=deb_pwin.plaintiff,
                               ntopic=com1.ntopic,
                               debate=deb_pwin,
                               pub_date=datetime.datetime.now(),
                               comment="Plaintiff win 2nd rebuttal")
    deb_pwin_com3.save()
    
    deb_pwin_vote1 = nVote(argument=deb_pwin,
                           voter=users[1],
                           voted_for='P')
    deb_pwin_vote1.save()

    deb_pwin_vote2 = nVote(argument=deb_pwin,
                           voter=users[2],
                           voted_for='P')
    deb_pwin_vote2.save()

    deb_pwin_vote3 = nVote(argument=deb_pwin,
                           voter=users[3],
                           voted_for='D')
    deb_pwin_vote3.save()

    # Debate ends in a draw, status = 5
    deb_draw = Debate(plaintiff=debaters[5],
                      defendant=com1.user,
                      status=5,
                      incite=com1,
                      title="Debate - Draw",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_draw.save()
    deb_draw_com1 = ArgComment(user=deb_draw.plaintiff,
                               ntopic=com1.ntopic,
                               debate=deb_draw,
                               pub_date=datetime.datetime.now(),
                               comment="Draw challenge")
    deb_draw_com1.save()

    deb_draw_com2 = ArgComment(user=deb_draw.defendant,
                               ntopic=com1.ntopic,
                               debate=deb_draw,
                               pub_date=datetime.datetime.now(),
                               comment="Draw 1st rebuttal")
    deb_draw_com2.save()

# Set up a blog
    bloguser = User.objects.all()[0]
    blog = Blog(author=bloguser,
                start_date=datetime.datetime(year=2009,
                                             month=1,
                                             day=1),
                title="The test blog",
                tagline_txt="The blog where we test bloggging",
                about_txt="All about running tests")
    blog.save()
    blog.start_date=datetime.datetime(year=2009,
                                      month=1,
                                      day=1)
    blog.save()

    for i in range(10):
        if i % 2:
           pd = None
        else:
            pd = datetime.datetime(year=2009,
                                   month=i+1,
                                   day=2)
        post = Post(title = "test post %i" % i,
                    txt = "lorem ipsum etc %i" % i,
                    created = datetime.datetime(year=2009,
                                                month=i+1,
                                                day=1),
                    pub_date = pd,
                    draft = i % 2 == 0,
                    tags = "test,tag%i, tag2%i" % (i, i),
                    blog=blog)
        post.save()
                                       

def create_user(username, password, email):
    new_user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
    new_user.is_staff=False
    new_user.is_superuser=False
    new_user.is_active=True
    new_user.save()

    prof = Profile(user=new_user,
                   score=0)
    prof.save()

    return new_user, prof

                                    
def create_topic(user, title, tags='', url='', comment=''):
    prof = Profile.objects.get(user=user)
    topic = Topic(user = user,
                  title=title,
                  score=1,
                  sub_date=datetime.datetime.now(),
                  comment_length=0,
                  last_calc=datetime.datetime.now(),
                  needs_review=prof.probation,
                  spam=prof.shadowban)
    topic.save()

    if url:
        topic.url=url
    else:
        topic.url = ''.join([HOSTNAME, '/', str(topic.id), '/'])

    dtags = tags
    if dtags:
        # create the count of all tags for the topic
        tags = '\n'.join([dtags, ','.join(['1']*(dtags.count(',')+1))])
        topic.tags = tags

        # create a Tags object to indicate the submitter
        # added these tags to this topic                        
        utags = Tags(user=user, topic=topic, tags=dtags)
        utags.save()

        # update the count of all tags used by the submitter
        prof.tags = update_tags(prof.tags, dtags.split(','))
        prof.save()

    topic.save()


    prof.last_post = topic.sub_date
    prof.save()

    if comment:
        comment = TopicComment(user=user,
                               ntopic=topic,
                               pub_date=datetime.datetime.now(),
                               comment=comment,
                               first=True,
                               nparent_id=0,
                               nnesting=0)
        comment.save()

        topic.comment_length += len(comment.comment)
        topic.recalculate()
        topic.save()

    return topic

def create_tcomment(user, top, txt, parent=None):

    prof = Profile.objects.get(user=user)

    params = {'comment': txt,
              'user': user,
              'ntopic': top,
              'needs_review': prof.probation,
              'spam': prof.shadowban}

    if parent:
        params['nparent_id'] = parent.id
        params['nnesting'] = parent.nnesting + 40
    else:
        params['nparent_id'] = 0
        params['nnesting'] = 10

    c = TopicComment(**params)
    c.save()		    

    top.comment_length += len(c.comment)
    top.recalculate()
    top.save()


    prof.last_post = c.pub_date
    prof.save()

    return c



    
