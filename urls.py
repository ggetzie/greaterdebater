from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'', include('tcd.items.urls')),                       
)
