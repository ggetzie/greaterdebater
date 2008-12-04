from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'^tcdsetup.html$', 'django.views.generic.simple.direct_to_template', {'template': 'tcdsetup.html'}),
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'', include('tcd.items.urls')),                       
)
