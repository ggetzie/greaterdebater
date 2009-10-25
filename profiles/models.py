from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
    newwin = models.BooleanField(default=False)
    mailok = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.user.username

class Forgotten(models.Model):
    """Temporarily associate a user with a randomly generated 32 character string.
When a forget password request is made, a url with this string will be emailed to
the user. When the user visits that url he will be able to reset his password. The
entry in this table should be deleted at that time."""
    user = models.ForeignKey(User)
    code = models.CharField(max_length=32, unique=True)
