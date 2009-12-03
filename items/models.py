from django.db import models
from django.contrib.auth.models import User
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
    tags = models.TextField(blank=True)

    
    class Meta:
        ordering = ['-sub_date']

    
    def __unicode__(self):
        return self.title
    
    def get_elapsed(self):
        return elapsed_time(self.sub_date)

    def recalculate(self):
        # a topic's score is (total length of all comments) / (hours elapsed since topic submitted)^2
        delta = datetime.datetime.now() - self.sub_date
        time = (delta.days * 24) + (delta.seconds / (60 * 60)) + 1 # add 1 to avoid dividing by zero
        self.score = self.comment_length / float(time * time)
        self.last_calc = datetime.datetime.now()

    def get_domain(self):
        domain = urlparse.urlparse(self.url)[1]
        if domain:
            return domain
        else:
            return "greaterdebater.com"

    def get_host(self):
        return HOSTNAME

    def display_tags(self):
        if self.tags:
            return self.tags.split('\n')[0].split(',')
        else:
            return []
        
    def get_absolute_url(self):
        return self.url

    def get_first_comment(self):
        com = self.comment_set.filter(is_first=True)
        if com:
            return com[0]
        else:
            return False

    def com_count(self):
        num = self.comment_set.filter(arg_proper=False, 
                                      is_removed=False,
                                      needs_review=False,
                                      is_msg=False).count()
        return num

    def resum(self):
        clen = 0
        coms = self.comment_set.filter(is_removed=False,
                                       needs_review=False,
                                       is_msg=False)

        for com in coms:
            clen += len(com.comment)
        self.comment_length = clen
        self.recalculate()
        self.save()
    

class Argument(models.Model):
    plaintiff = models.ForeignKey(User, related_name='plaintiff_set')
    defendant = models.ForeignKey(User, related_name='defendant_set')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=140)
    # status codes: 0 = challenge made, response pending
    #               1 = argument in progress, plaintiff's turn
    #               2 = argument in progress, defendant's turn
    #               3 = argument over, defendant won
    #               4 = argument over, plaintiff won
    #               5 = argument over, draw
    #               6 = plaintiff declined challenge
    #               others invalid
    status = models.PositiveSmallIntegerField(default=0)
    score = models.FloatField(default=0)

    
    class Meta:
        ordering = ['-score', '-start_date']

    
    def __unicode__(self):
        return self.title
    
    def get_status(self):
        if self.status == 0:
            # challenge offered, defendent's turnn
            return "challenge pending"
        elif self.status == 1:
            # argument in progress, plaintiff's turn
            return ''.join([self.plaintiff.username, "'s turn"])
        elif self.status == 2:
            # argument in progress, defendants's turn
            return ''.join([self.defendant.username, "'s turn"])
        elif self.status == 3:
            # argument over, defendant wins
            return ''.join([self.defendant.username, " wins!"])
        elif self.status == 4:
            # argument over, plaintiff wins
            return ''.join([self.plaintiff.username, " wins!"])
        elif self.status == 5:
            # opponents agreed to a draw
            return "draw"
        elif self.status == 6:
            # argument never started, defendant declined challenge
            return ''.join([ self.defendant.username, " declined challenge"])
        else:
            return "invalid status"        
    
    def whos_up(self, invert=0):
        # returns the user whose turn it is in an argument
        # if invert == 1, returns the user whose turn it is NOT
        participants = (self.defendant, self.plaintiff)
        if self.status in [0, 2]:
            return participants[invert]
        elif self.status == 1:
            return participants[1-invert]
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

    def reset(self):
        # Get the winner and reduce his score by one
        winner = None
        if self.status == 3:
            winner = self.defendant
        elif self.status == 4:
            winner = self.plaintiff
        else:
            return "Argument cannot be reset, no winner"
        prof = Profile.objects.get(user = winner)
        prof.score -= 1
        prof.save()

        # Set the status of the argument so it's the loser's turn again
        self.status -= 2
        self.save()

    def calculate_score(self):
        numvotes = Vote.objects.filter(argument=self.id).count()
        delta = datetime.datetime.now() - self.start_date
        hours2 = (delta.days*24 + delta.seconds/(3600) + 1.0)**2
        self.score = float(numvotes / hours2)
        self.save()

    def first_two(self):
        # The initial comment that inspired the argument
        # and the first assault by the plaintiff
        return self.comment_set.order_by('pub_date')[:2]

    def get_absolute_url(self):
        return '/'.join([HOSTNAME, 'argue', str(self.id)])


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


class Tags(models.Model):

    topic = models.ForeignKey(Topic, related_name="tagged_topic")
    user = models.ForeignKey(User)
    tags = models.TextField()

    def display_tags(self):
        return self.tags.split(',')
