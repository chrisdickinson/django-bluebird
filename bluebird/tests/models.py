from ..managers import TwitterIdentificationManager
from ..models import TwitterConsumer, TwitterIdentification, TwitterProfile
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.test import TestCase
import waiter
from waiter.apis.twitter import TwitterMenu
import mox
import random
import oauth2
from django.utils import simplejson


def RANDOM():
    return random.randint(1,100)

def RANDOMSTR(string='rand'):
    return string+str(RANDOM())

class TestOfTwitterConsumer(TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_get_auth_portal_calls_get_current(self):
        site_manager_mock = self.mox.CreateMock(Site.objects)
        random_value = RANDOM()
        class MockSite(object):
            twitter_auth_portal = random_value
        site_manager_mock.get_current().AndReturn(MockSite())
        self.mox.ReplayAll()
        result = TwitterConsumer.get_auth_portal(site_manager_mock)
        self.assertEqual(result, random_value)
        self.mox.VerifyAll()

    def test_get_current_calls_get_current_and_twitter_consumers(self):
        mock_return_array = [RANDOM()]
        consumer_manager_mock = self.mox.CreateMock(TwitterConsumer.objects)
        site_mock = self.mox.CreateMock(Site)
        site_mock.twitter_consumers = consumer_manager_mock 
        site_manager_mock = self.mox.CreateMock(Site.objects)
        site_manager_mock.get_current().AndReturn(site_mock)
        consumer_manager_mock.all().AndReturn(mock_return_array)
        self.mox.ReplayAll()
        result = TwitterConsumer.get_current_consumer(site_manager_mock)
        self.assertEqual(result, mock_return_array[0])
        self.mox.VerifyAll()

    def test_get_current_site_gets_current_site(self):
        random_value = RANDOM()
        site_manager_mock = self.mox.CreateMock(Site.objects)
        site_manager_mock.get_current().AndReturn(random_value)
        self.mox.ReplayAll()
        result = TwitterConsumer().get_current_site(site_manager_mock)
        self.assertEqual(result, random_value)
        self.mox.VerifyAll()

    def test_get_client_returns_oauth2_client(self):
        random_key = RANDOMSTR()
        random_secret = RANDOMSTR()
        tc = TwitterConsumer(key=random_key, secret=random_secret)
        random_return = RANDOM()
        results = tc.get_client()
        self.assertTrue(isinstance(results, oauth2.Client))
        self.assertEqual(results.consumer.key, random_key)

    def test_get_request_token_from_twitter(self):
        """
            some... unorthodox mocking follows. my apologies.
        """
        mock_http = RANDOM()
        random_value = RANDOM()
        class MockWaiter(waiter.Waiter):
            expected_calls = [{}, 'https://twitter.com/oauth/request_token', mock_http]
            def __div__(_self, rhs):
                cmp = _self.expected_calls.pop()
                self.assertEqual(cmp, rhs)
                return _self
        mock_waiter = MockWaiter()
        old_oauth_from_string = oauth2.Token.from_string
        self.mox.StubOutWithMock(oauth2.Token, 'from_string')
        oauth2.Token.from_string(mock_waiter).AndReturn(random_value)
        tc = TwitterConsumer()
        self.mox.ReplayAll()
        results = tc.get_request_token_from_twitter(mock_http, mock_waiter)
        self.assertEqual(results, random_value)
        self.mox.VerifyAll()
        oauth2.Token.from_string = old_oauth_from_string

    def test_get_access_token_from_twitter(self):
        mock_http = RANDOM()
        random_value = RANDOM()
        random_oauth_token_val = RANDOM()
        class MockWaiter(waiter.Waiter):
            expected_calls = [{'oauth_token':random_oauth_token_val}, 'https://twitter.com/oauth/access_token', mock_http]
            def __div__(_self, rhs):
                cmp = _self.expected_calls.pop()
                self.assertEqual(cmp, rhs)
                return _self
        mock_waiter = MockWaiter()
        old_oauth_from_string = oauth2.Token.from_string
        self.mox.StubOutWithMock(oauth2.Token, 'from_string')
        oauth2.Token.from_string(mock_waiter).AndReturn(random_value)
        tc = TwitterConsumer()
        self.mox.ReplayAll()
        results = tc.get_access_token_from_twitter('anything', random_oauth_token_val, mock_http, mock_waiter)
        self.assertEqual(results, random_value)
        self.mox.VerifyAll()
        oauth2.Token.from_string = old_oauth_from_string

class TestOfTwitterIdentification(TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_get_client_delegates_to_consumer(self):
        random_oauth_token = oauth2.Token(RANDOMSTR(), RANDOMSTR())
        ti = TwitterIdentification()
        ti.oauth_token = random_oauth_token
        expected_oauth_token = ti.oauth_token
        mock_consumer = self.mox.CreateMock(TwitterConsumer)
        mock_consumer.id = RANDOM()
        ti.consumer = mock_consumer
        random_value = RANDOM()
        ti.consumer.get_client(expected_oauth_token).AndReturn(random_value)
        self.mox.ReplayAll()
        results = ti.get_client()
        self.assertEqual(results, random_value)
        self.mox.VerifyAll()


class TestOfTwitterProfile(TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_unpack_data_delegates_to_simplejson(self):
        random_data = RANDOMSTR()
        random_dict = {
            RANDOMSTR():RANDOM()
        }
        self.mox.StubOutWithMock(simplejson, 'loads')
        simplejson.loads(random_data).AndReturn(random_dict)
        tp = TwitterProfile(raw_data=random_data)
        self.mox.ReplayAll()
        result = tp.unpack_data()
        self.assertEqual(result.__class__.__name__, 'TwitterProfileProxy')
        self.assertTrue(hasattr(result, random_dict.keys()[0]))
        self.assertEqual(getattr(result, random_dict.keys()[0]), random_dict.values()[0])
        self.mox.VerifyAll()

    def test_pack_data_avoids_builtins(self):
        random_key = RANDOMSTR()
        raw_data = {
            random_key:RANDOM(),
            '__div__':RANDOM(), 
        }
        raw_data_as_json = simplejson.dumps(raw_data)
        tp = TwitterProfile(raw_data=raw_data_as_json)
        tp.data
        self.assertTrue(hasattr(tp.data, '__div__'))
        packed_data = tp.pack_data()
        unpacked_again = simplejson.loads(packed_data)
        self.assertRaises(KeyError, unpacked_again.__getitem__, '__div__')
        self.assertEqual(unpacked_again[random_key], raw_data[random_key])
