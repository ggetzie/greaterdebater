from django.contrib.auth.models import User
from django.db import models

from tcd.settings import HOSTNAME
from tcd.base_utils import wordtime

import datetime

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
    newwin = models.BooleanField(default=False)
    mailok = models.BooleanField(default=False)
    
    # all tags used by this user
    tags = models.TextField(blank=True)
    last_post = models.DateTimeField(default=datetime.datetime(month=1, day=1, year=1970))

    # Level of infraction into rate limiting
    rate = models.PositiveSmallIntegerField(default=0)

    # items to include in the user's personal RSS feed
    feedcoms = models.BooleanField(default=False)
    feedtops = models.BooleanField(default=False)
    feeddebs = models.BooleanField(default=False)

    # Always follow user's own topics or comments?
    followtops = models.BooleanField(default=True)
    followcoms = models.BooleanField(default=True)

    # New user still in probationary period, 
    # topics and comments need review
    probation = models.BooleanField(default=True)

    # Send users topics and comment silently to the round file
    shadowban = models.BooleanField(default=False)
    
    # Post user's submissions to @GreaterDebater and the Facebook page?
    socmed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.user.username

    def check_rate(self):
        def calc_timeout(rate):
            return 2 + 2**(2*rate)

        if self.rate > 8: 
            return "Your account has been locked. Please contact admin@greaterdebater.com"

        if not self.last_post: return ""

        delta = datetime.datetime.now() - self.last_post
        if delta.days > 0: return ""

        timeout = calc_timeout(self.rate)
        if delta.seconds < timeout:
            self.rate += 1
            timeout = calc_timeout(self.rate)
            self.save()
            if self.rate > 8: 
                return "Your account has been locked. Please contact admin@greaterdebater.com"
            else:
                return ''.join(["Post rate limit exceeded<br />",
                                "Please wait ", wordtime(timeout),
                                " before submitting another comment or topic"])
        else:
            self.rate = 0
            self.save()
            return ""

    def get_absolute_url(self):
        return '/'.join([HOSTNAME, 'users', 'u', self.user.username, 'profile'])

    def has_feed(self):
        return self.feedcoms or self.feedtops or self.feeddebs

    def feedurl(self):
        return '/'.join([HOSTNAME, 'feeds', 'user', self.user.username, ''])

    def atomfeedurl(self):
        return '/'.join([HOSTNAME, 'atom', 'user', self.user.username, ''])

class Forgotten(models.Model):
    """Temporarily associate a user with a randomly generated 32 character string.
    When a forget password request is made, a url with this string will be emailed to
    the user. When the user visits that url he will be able to reset his password. The
    entry in this table should be deleted at that time."""
    user = models.ForeignKey(User)
    code = models.CharField(max_length=32, unique=True)


