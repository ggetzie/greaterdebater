import os
import sys
import site

site.addsitedir('/usr/local/src/env/tcd/lib/python2.7/site-packages')

path = '/usr/local/src/tcd/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()