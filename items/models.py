from django.db import models
from django.contrib.auth.models import User
from tcd.utils import elapsed_time

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
    tflaggers = models.ManyToManyField(User, verbose_name="Users who flagged this topic as spam", related_name='tflaggers_set')
    needs_review = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['-sub_date']


    def __unicode__(self):
        return self.title
    
    def get_elapsed(self):
        return elapsed_time(self.sub_date)

    def recalculate(self):
        # a topic's score is (total length of all comments) / (minutes elapsed since topic submitted)
        delta = datetime.datetime.now() - self.sub_date
        time = (delta.days * 1440) + (delta.seconds / 60) + 1 # add 1 to avoid dividing by zero
        self.score = self.comment_length / float(time)
        self.last_calc = datetime.datetime.now()

    def get_domain(self):
        domain = urlparse.urlparse(self.url)[1]
        if domain:
            return domain
        else:
            return "greaterdebater.com"

class Argument(models.Model):
    plaintiff = models.ForeignKey(User, related_name='plaintiff_set')
    defendant = models.ForeignKey(User, related_name='defendant_set')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=200)
    # status codes: 0 = challenge made, response pending
    #               1 = argument in progress, plaintiff's turn
    #               2 = argument in progress, defendant's turn
    #               3 = argument over, defendant won
    #               4 = argument over, plaintiff won
    #               5 = argument over, draw
    #               6 = plaintiff declined challenge
    #               others invalid
    status = models.PositiveSmallIntegerField(default=0)

    
    class Meta:
        ordering = ['-start_date']

    
    def __unicode__(self):
        return self.title
    
    def get_status(self):
        if self.status == 0:
            return "challenge pending"
        elif self.status == 1:
            return ''.join([self.plaintiff.username, "'s turn"])
        elif self.status == 2:
            return ''.join([self.defendant.username, "'s turn"])
        elif self.status == 3:
            return ''.join([self.defendant.username, " wins!"])
        elif self.status == 4:
            return ''.join([self.plaintiff.username, " wins!"])
        elif self.status == 5:
            return "draw"
        elif self.status == 6:
            return ''.join([ self.defendant.username, " declined challenge"])
        else:
            return "invalid status"        
    
    def whos_up(self):
        if self.status in [0, 2]:
            return self.defendant
        elif self.status == 1:
            return self.plaintiff
        else:
            return None

    def get_opponent(self, user):
        if user == self.defendant:
            return self.plaintiff
        elif user == self.plaintiff:
            return self.defendant
        else:
            return None

    def get_elapsed(self):
        return elapsed_time(self.start_date)


class LogItem(models.Model):
    date = models.DateTimeField()
    message = models.CharField(max_length=200)

    def __unicode__(self):
        return self.message


class Vote(models.Model):

    argument = models.ForeignKey(Argument)
    voter = models.ForeignKey(User)
    voted_for = models.CharField(max_length=1) # "P" for plaintiff or "D" for defendant
    
    def __unicode__(self):
        return ' '.join([self.voter.username, "voted for", self.voted_for, "in arg", self.argument.title])

