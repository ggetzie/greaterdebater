from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    title = models.CharField(max_length=200)
    sub_date = models.DateTimeField('date submitted')
    score = models.IntegerField()
    url = models.URLField()
    user = models.ForeignKey(User)

    
    class Admin:
        pass


    class Meta:
        ordering = ['-score', '-sub_date']

    def __unicode__(self):
        return self.title


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
    
    def __unicode__(self):
        return str(self.id)
    
    def get_status(self):
        if self.status == 0:
            return "challenge pending"
        elif self.status == 1:
            return "in progress, plaintiff's turn"
        elif self.status == 2:
            return "in progress, defendant's turn"
        elif self.status == 3:
            return ''.join(["winner: ", self.defendant.username])
        elif self.status == 4:
            return ''.join(["winner: ", self.plaintiff.username])
        elif self.status == 5:
            return "opponents agreed to a draw"
        elif self.status == 6:
            return "plaintiff declined challenge"
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
