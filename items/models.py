from django.db import models
from django.contrib.auth.models import User
from django.template import loader, Context

from tcd.profiles.models import Profile
from tcd.utils import elapsed_time
from tcd.settings import HOSTNAME

import datetime
import urlparse

class Topic(models.Model):
    title = models.CharField(max_length=200)
    sub_date = models.DateTimeField('date submitted')
    score = models.FloatField()
    url = models.URLField()
    user = models.ForeignKey(User)
    comment_length = models.IntegerField()
    last_calc = models.DateTimeField('last score calculation')
    tflaggers = models.ManyToManyField(User, 
                                       verbose_name="Users who flagged this topic as spam", 
                                       related_name='tflaggers_set',
                                       blank=True)
    needs_review = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)
    tags = models.TextField(blank=True)

    followers = models.ManyToManyField(User,
                                       verbose_name="Users following this topic",
                                       related_name="tfollow_set",
                                       blank=True)

    
    class Meta:
        ordering = ['-sub_date']

    
    def __unicode__(self):
        return self.title
    
    def get_elapsed(self):
        return elapsed_time(self.sub_date)

    def recalculate(self):
        if self.spam:
            self.score = 0
        else:
            # a topic's score is (total length of all comments) / (hours elapsed since topic submitted)^2
            delta = datetime.datetime.now() - self.sub_date
            time = (delta.days * 24) + (delta.seconds / (60 * 60)) + 1 # add 1 to avoid dividing by zero
            self.score = self.comment_length / float(time * time)
            self.last_calc = datetime.datetime.now()

    def get_domain(self):
        return urlparse.urlparse(self.url)[1]

    def get_comments_url(self):
        return ''.join([HOSTNAME, '/', str(self.id), '/'])

    def display_tags(self):
        if self.tags:
            return self.tags.split('\n')[0].split(',')
        else:
            return []
        
    def get_absolute_url(self):
        return self.url

    def get_first_comment(self):
        com = self.topiccomment_set.filter(first=True)
        if com:
            return com[0]
        else:
            return False

    def com_count(self):
        num = self.topiccomment_set.filter(removed=False,
                                           needs_review=False).count()
        return num

    def resum(self):
        clen = 0
        coms = self.topiccomment_set.filter(removed=False,
                                            needs_review=False)
        acoms = self.argcomment_set.all()


        for com in coms | acoms:
            clen += len(com.comment)
        self.comment_length = clen
        self.recalculate()
        self.save()

    def get_date(self):
        return self.sub_date

    def get_description(self):
        dest = loader.get_template('feeds/newtopics_description.html')
        desc = Context({'obj': self})
        return dest.render(desc)

    def get_title(self):
        return self.title

    
class LogItem(models.Model):
    date = models.DateTimeField()
    message = models.CharField(max_length=200)

    def __unicode__(self):
        return self.message


class Tags(models.Model):

    topic = models.ForeignKey(Topic, related_name="tagged_topic")
    user = models.ForeignKey(User)
    tags = models.TextField()

    def display_tags(self):
        return self.tags.split(',')

    def __unicode__(self):
        return self.tags

    
