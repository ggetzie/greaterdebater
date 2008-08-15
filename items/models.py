from django.db import models
from django.contrib.auth.models import User
import datetime

class Topic(models.Model):
    title = models.CharField(max_length=200)
    sub_date = models.DateTimeField('date submitted')
    score = models.FloatField()
    url = models.URLField()
    user = models.ForeignKey(User)
    comment_length = models.IntegerField()
    last_calc = models.DateTimeField('last score calculation')
    
    class Admin:
        pass


    class Meta:
        ordering = ['-score', '-sub_date']

    def __unicode__(self):
        return self.title
    
    def get_elapsed(self):
        return elapsed_time(self.sub_date)

    def recalculate(self):
        delta = datetime.datetime.now() - self.sub_date
        time = (delta.days * 1440) + (delta.seconds / 60) + 1
        self.score = self.comment_length / float(time)
        self.last_calc = datetime.datetime.now()

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

    
    class Admin:
        pass

    class Meta:
        ordering = ['-start_date']
    
    def __unicode__(self):
        return self.title
    
    def get_status(self):
        if self.status == 0:
            return "challenge pending"
        elif self.status == 1:
            return ''.join(["in progress, ", self.plaintiff.username, "'s turn"])
        elif self.status == 2:
            return ''.join(["in progress, ", self.defendant.username, "'s turn"])
        elif self.status == 3:
            return ''.join(["winner: ", self.defendant.username])
        elif self.status == 4:
            return ''.join(["winner: ", self.plaintiff.username])
        elif self.status == 5:
            return "opponents agreed to a draw"
        elif self.status == 6:
            return ''.join([ self.plaintiff.username, " declined challenge"])
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

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
    
    class Admin:
        pass

    def __unicode__(self):
        return self.user.username

def elapsed_time(dtime):
    delta = datetime.datetime.now() - dtime
    if delta.days > 0:
        return ''.join([str(delta.days), " days"])
    elif delta.seconds > 3600:
        return ''.join([str(delta.seconds / 3600), " hours"])
    elif 3600 > delta.seconds >= 60:
        return ''.join([str(delta.seconds / 60), " minutes"])
    elif 60 > delta.seconds >= 1:
        return ''.join([str(delta.seconds), " seconds"])
    elif delta.seconds == 0:
        return ''.join([str(delta.microseconds / 1000), " milliseconds"])
    else:
        return "0 milliseconds"

class LogItem(models.Model):
    date = models.DateTimeField()
    message = models.CharField(max_length=200)

    def __unicode__(self):
        return self.message


