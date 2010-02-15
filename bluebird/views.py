from .models import TwitterConsumer
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import urllib

TWITTER_REQUEST_TOKEN_KEY = 'bluebird.request_token'
TWITTER_REDIRECT_KEY = 'next'

def initiate_login_on_site(request):
    try:
        current_consumer = TwitterConsumer.get_current_consumer()
        current_site = current_consumer.get_current_site()

        redirect_after_login = request.GET.get(TWITTER_REDIRECT_KEY, '')
        redirect_after_login = 'http://' + (''.join([current_site.domain, redirect_after_login]))
        redirect_to = ''.join([current_consumer.auth_portal.domain, reverse('bluebird_auth_initiate_login')])
        redirect_to = '?'.join([redirect_to, urllib.urlencode({TWITTER_REDIRECT_KEY:redirect_after_login})])
        return HttpResponseRedirect('http://'+redirect_to)
    except TwitterConsumer.DoesNotExist:
        raise Http404

def initiate_login_on_auth_portal(request):
    if not getattr(settings, 'IS_BLUEBIRD_AUTH_PORTAL', False):
        raise Http404
    try:
        current_consumer = TwitterConsumer.get_auth_portal()
        current_site = current_consumer.get_current_site()

        request_token = current_consumer.get_request_token_from_twitter()
        redirect_to = request.GET.get(TWITTER_REDIRECT_KEY, '')
        request.session[TWITTER_REQUEST_TOKEN_KEY] = request_token
        request.session[TWITTER_REDIRECT_KEY] = redirect_to
        twitter_auth = 'https://twitter.com/oauth/authorize?oauth_token=%s' % request_token.key
        return HttpResponseRedirect(twitter_auth)
    except TwitterConsumer.DoesNotExist:
        raise Http404

def login_on_auth_portal(request):
    try:
        if not getattr(settings, 'IS_BLUEBIRD_AUTH_PORTAL', False):
            raise Http404
        user = auth.authenticate(twitter_request=request)
        if user:
            auth.login(request, user)
        redirect = request.session[TWITTER_REDIRECT_KEY]
        request.session[TWITTER_REDIRECT_KEY] = None
        return HttpResponseRedirect(redirect)
    except KeyError:
        raise Http404
