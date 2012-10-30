from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import hyperadmin
hyperadmin.site.install_models_from_site(admin.site) #ports admin models to hyperadmin
hyperadmin.site.install_storage_resources() #enables the storage resource for media and static
hyperadmin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'hostingservices.views.home', name='home'),
    # url(r'^cmsdemo/', include('cmsdemo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hyperapi/', include(hyperadmin.site.urls)),
    url(r'^hyperadmin/', include('hyperadminclient.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('', (r'', include('django.contrib.staticfiles.urls')))

    urlpatterns += patterns('django.views',
        (r'^media/(?P<path>.*)$', 'static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

