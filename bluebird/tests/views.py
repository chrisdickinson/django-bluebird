from ..managers import TwitterIdentificationManager
from ..models import TwitterConsumer, TwitterIdentification, TwitterProfile
from ..views import initiate_login_on_site, initiate_login_on_auth_portal, login_on_auth_portal, TWITTER_REDIRECT_KEY
from django.contrib import auth
from django.conf import settings
from django.http import Http404
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, RegexURLResolver
from django.test import TestCase
import waiter
from waiter.apis.twitter import TwitterMenu
import mox
import urllib
import random
import oauth2
from django.utils import simplejson

test_class = TestCase

try:
    resolver = RegexURLResolver(r'^/', settings.ROOT_URLCONF)
    resolver.resolve404()
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    try:
        get_template('404.html')
    except TemplateDoesNotExist:
        test_class = object
        print """
            *** bluebird.tests.views.py *** 
            To run these tests you must define a 404.html in one of your template
            directories.
        """.strip()
        print "*"*80
        raw_input("Press enter to continue: ")
except AttributeError:
    test_class = object
    print """
        *** bluebird.tests.views.py ***
        To run these tests you must define a handler404 view in your root urls.py.
        A sensible default is to add the following line to your project urls.py:
            ``from django.conf.urls.defaults import handler404``    
    """.strip()
    print "*"*80
    raw_input("Press enter to continue: ")

def RANDOM():
    return random.randint(1,100)

def RANDOMSTR(string='rand'):
    return string+str(RANDOM())

class TestOfBluebirdViews(test_class):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_initiate_login_raises_404_on_no_consumers(self):
        response = self.client.get(reverse('bluebird_initiate_login'))
        self.assertEqual(response.status_code, 404)

    def test_initiate_login_on_auth_portal_raises_404_on_nonauth_portal(self):
        settings.IS_BLUEBIRD_AUTH_PORTAL = False
        response = self.client.get(reverse('bluebird_auth_initiate_login'))
        self.assertEqual(response.status_code, 404)

    def test_initiate_login_on_auth_portal_raises_404_on_no_consumers(self):
        settings.IS_BLUEBIRD_AUTH_PORTAL = True 
        response = self.client.get(reverse('bluebird_auth_initiate_login'))
        self.assertEqual(response.status_code, 404)

    def test_login_raises_404_on_nonauth_portal(self):
        settings.IS_BLUEBIRD_AUTH_PORTAL = False
        response = self.client.get(reverse('bluebird_login'))
        self.assertEqual(response.status_code, 404)

    def test_initiate_login_redirects(self):
        auth_site = Site.objects.create(
            domain='%s.com'%RANDOMSTR(),
            name=RANDOMSTR()
        )
        other_site = Site.objects.create(
            domain='other-%s.com'%RANDOMSTR(),
            name=RANDOMSTR(),
        )
        consumer = other_site.twitter_consumers.create(
            key=RANDOMSTR(),
            secret=RANDOMSTR(),
            auth_portal=auth_site
        )
        settings.SITE_ID = other_site.pk
        next_view = RANDOMSTR()

        response = self.client.get(reverse('bluebird_initiate_login')+('?next=%s'%next_view))
        self.assertEqual(response.status_code, 302)
        loc, location = response._headers['location']
        expected = "http://%s?%s" % (auth_site.domain + reverse('bluebird_auth_initiate_login'), urllib.urlencode({'next':''.join(['http://'+other_site.domain, next_view])}))
        self.assertEqual(location, expected)

    def test_login_redirects(self):
        random_redirect = RANDOMSTR()
        class MockRequest(object):
            session = {
                TWITTER_REDIRECT_KEY:random_redirect
            }
        mock_request = MockRequest()
        self.mox.StubOutWithMock(auth, 'authenticate')
        self.mox.StubOutWithMock(auth, 'login')
        settings.IS_BLUEBIRD_AUTH_PORTAL = True
        random_user = RANDOMSTR()
        auth.authenticate(twitter_request=mock_request).AndReturn(random_user)
        auth.login(mock_request, random_user)
        self.mox.ReplayAll()
        result = login_on_auth_portal(mock_request)
        self.assertEqual(result.status_code, 302)
        loc, location = result._headers['location']
        self.assertEqual(location, random_redirect)
        self.mox.VerifyAll()

    def test_login_404s_on_no_redirect(self):
        random_redirect = RANDOMSTR()
        class MockRequest(object):
            session = {}
        mock_request = MockRequest()
        self.mox.StubOutWithMock(auth, 'authenticate')
        self.mox.StubOutWithMock(auth, 'login')
        settings.IS_BLUEBIRD_AUTH_PORTAL = True
        random_user = RANDOMSTR()
        auth.authenticate(twitter_request=mock_request).AndReturn(random_user)
        auth.login(mock_request, random_user)
        self.mox.ReplayAll()
        result = self.assertRaises(Http404, login_on_auth_portal, mock_request)
        self.mox.VerifyAll()

    def test_initiate_login_on_auth_redirects(self):
        settings.IS_BLUEBIRD_AUTH_PORTAL = True
        auth_site = Site.objects.create(
            domain='%s.com'%RANDOMSTR(),
            name=RANDOMSTR()
        )
        request_token = oauth2.Token(RANDOMSTR(), RANDOMSTR())
        random_redirect = RANDOMSTR()

        self.mox.StubOutWithMock(TwitterConsumer, 'get_auth_portal')
        mock_consumer = self.mox.CreateMock(TwitterConsumer)
        TwitterConsumer.get_auth_portal().AndReturn(mock_consumer)
        mock_consumer.get_current_site().AndReturn(auth_site)
        mock_consumer.get_request_token_from_twitter().AndReturn(request_token)
        self.mox.ReplayAll()
        response = self.client.get(reverse('bluebird_auth_initiate_login')+"?"+urllib.urlencode({TWITTER_REDIRECT_KEY:random_redirect}))

        self.assertEqual(response.status_code, 302)
        expected = 'https://twitter.com/oauth/authorize?oauth_token=%s'%request_token.key
        self.assertEqual(response._headers['location'][1], expected)
        self.mox.VerifyAll()
