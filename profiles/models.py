from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    score = models.IntegerField()
    
    class Admin:
        pass

    def __unicode__(self):
        return self.user.username
