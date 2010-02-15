from django.conf.urls.defaults import patterns, include, handler500, url

urlpatterns = patterns(
    'bluebird.views',
    url('^initiate_login', 'initiate_login_on_site', name='bluebird_initiate_login'),
    url('^portal_start_login', 'initiate_login_on_auth_portal', name='bluebird_auth_initiate_login'),
    url('^login', 'login_on_auth_portal', name='bluebird_login'),
)
