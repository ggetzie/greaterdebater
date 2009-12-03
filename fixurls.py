import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.comments.models import Topic
from tcd.settings import HOSTNAME

import datetime

def fixurls():
    tops = Topic.objects.all()
    for top in tops:
        if top.get_domain() == "greaterdebater.com":
            top.url = HOSTNAME + top.url
            top.save()

if __name__ == "__main__":
    fixurls()
