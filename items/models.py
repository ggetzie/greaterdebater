from django.db import models
from django.contrib.auth.models import User

# trivial change
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
