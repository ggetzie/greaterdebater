from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^tcdsetup.html$', 'django.views.generic.simple.direct_to_template', {'template': 'tcdsetup.html'}),
                       (r'^vinepics.html$', 'django.views.generic.simple.direct_to_template', {'template': 'vinepics.html'}),
                       (r'^admin/(.*)', admin.site.root),
                       (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
                       (r'^FAQ/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}),
                       (r'^help/$', 'django.views.generic.simple.direct_to_template', {'template': 'help.html'}),                       
                       (r'^tos/$', 'django.views.generic.simple.direct_to_template', {'template': 'tos.html'}),
                       (r'^privacy/$', 'django.views.generic.simple.direct_to_template', {'template': 'privacy.html'}),
                       (r'', include('tcd.items.urls'))
)
