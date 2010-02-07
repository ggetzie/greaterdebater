from django.db import models
from django.contrib.auth.models import User

from tcd.utils import wordtime

import datetime

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
    newwin = models.BooleanField(default=False)
    mailok = models.BooleanField(default=False)
    tags = models.TextField(blank=True)
    last_post = models.DateTimeField(blank=True)
    rate = models.PositiveSmallIntegerField(default=0)
    
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
        

class Forgotten(models.Model):
    """Temporarily associate a user with a randomly generated 32 character string.
    When a forget password request is made, a url with this string will be emailed to
    the user. When the user visits that url he will be able to reset his password. The
    entry in this table should be deleted at that time."""
    user = models.ForeignKey(User)
    code = models.CharField(max_length=32, unique=True)


