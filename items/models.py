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
    plaintiff = models.ForeignKey(User, related_name='plaintiff')
    defendant = models.ForeignKey(User, related_name='defendant')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True)
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=200)
    # status codes: 0 = argument still ongoing
    #               1 = argument over, plaintiff won
    #               2 = argument over, defendant won
    #               others invalid
    status = models.PositiveSmallIntegerField(default=0)
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.title

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
