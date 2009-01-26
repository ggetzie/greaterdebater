from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'^tcdsetup.html$', 'django.views.generic.simple.direct_to_template', {'template': 'tcdsetup.html'}),
                       (r'^vinepics.html$', 'django.views.generic.simple.direct_to_template', {'template': 'vinepics.html'}),
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'', include('tcd.items.urls')),                       
                       (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
                       (r'^FAQ/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}),
                       (r'^help/$', 'django.views.generic.simple.direct_to_template', {'template': 'help.html'}),
                       (r'^feedback/$', 'django.views.generic.simple.direct_to_template', {'template': 'feedback.html'}),
                       (r'^tos/$', 'django.views.generic.simple.direct_to_template', {'template': 'tos.html'}),
)
