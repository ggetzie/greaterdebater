import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.profiles.models import Profile
from tcd.items.models import Tags
from tcd.utils import tag_string, tag_dict

def utagsetup():
    allprofs = Profile.objects.all()
    for prof in allprofs:
        print "%s's profile" % prof.user.username
        td = tag_dict(prof.tags)
        utags = Tags.objects.filter(user=prof.user)
        for thistags in utags:
            for ut in thistags.tags.split(','):
                if ut in td:
                    td[ut] += 1
                else:
                    td[ut] = 1

        prof.tags = tag_string(td)
        prof.save()

if __name__ == "__main__":
    utagsetup()
            
            
