from django.db import models

class Tweet(models.Model):
    status = models.CharField(max_length=200)
    posted = models.DateTimeField('date posted')
    tweet_id = models.BigIntegerField()
    tweeter = models.ForeignKey('Account')

class Account(models.Model):
    screen_name = models.CharField(max_length=16)
    last_checked = models.DateTimeField()
    twitter_id = models.BigIntegerField()
