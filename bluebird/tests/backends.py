from ..managers import TwitterIdentificationManager
from ..models import TwitterConsumer, TwitterIdentification, TwitterProfile
from ..backends import TwitterAuthBackend
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.test import TestCase
import waiter
from waiter.apis.twitter import TwitterMenu, TwitterException
import mox
import random
import oauth2
from django.utils import simplejson


def RANDOM():
    return random.randint(1,100)

def RANDOMSTR(string='rand'):
    return string+str(RANDOM())

class TestOfTwitterAuthBackend(TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_init_initializes_correctly(self):
        random_twitter_manager = RANDOM()
        random_consumer_class = RANDOM()
        random_api_class = RANDOM()
        tb = TwitterAuthBackend(random_consumer_class, random_twitter_manager, random_api_class)
        self.assertEqual(tb.twitter_manager, random_twitter_manager)
        self.assertEqual(tb.consumer_class, random_consumer_class)
        self.assertEqual(tb.api_class, random_api_class)

    def test_authenticate_returns_none_on_bad_credentials(self):
        bad_credentials = { RANDOMSTR(): RANDOM() }
        tb = TwitterAuthBackend()
        results = tb.authenticate(**bad_credentials)
        self.assertEqual(results, None)

    def test_authenticate_returns_none_on_no_oauth_token(self):
        class MockRequest(object):
            GET = {}
        credentials = { 
            'twitter_request':MockRequest()
        }
        tb = TwitterAuthBackend()
        results = tb.authenticate(**credentials)
        self.assertEqual(results, None)

    def test_authenticate_returns_none_on_no_request_token(self):
        class MockRequest(object):
            GET = {'oauth_token':RANDOMSTR()}
            session = {}
        credentials = { 
            'twitter_request':MockRequest()
        }
        tb = TwitterAuthBackend()
        results = tb.authenticate(**credentials)
        self.assertEqual(results, None)

    def test_continue_authentication_returns_none_on_twitter_exception(self):
        mock_http = RANDOMSTR()
        class MockWaiter(object):
            expected_methods = [{}, 'account/verify_credentials.json', mock_http]
            def __div__(mock, rhs):
                cmp = mock.expected_methods.pop()
                self.assertEqual(cmp, rhs)
                if not mock.expected_methods:
                    raise TwitterException
                return mock 

        random_request_token = RANDOM()
        random_oauth_token = RANDOM()
        random_access_token = RANDOM()
        old_get_auth_portal = TwitterConsumer.get_auth_portal
        self.mox.StubOutWithMock(TwitterConsumer, 'get_auth_portal')
        mock_consumer_class = TwitterConsumer
        mock_consumer = self.mox.CreateMock(TwitterConsumer)
        mock_consumer_class.get_auth_portal().AndReturn(mock_consumer)
        mock_consumer.get_access_token_from_twitter(random_request_token, random_oauth_token).AndReturn(random_access_token)
        mock_consumer.get_client(random_access_token).AndReturn(mock_http)
        self.mox.ReplayAll()
        tp = TwitterAuthBackend(mock_consumer_class, RANDOM(), MockWaiter)
        result = tp.continue_authentication(random_request_token, random_oauth_token)
        self.assertEqual(result, None)
        self.mox.VerifyAll()
        TwitterConsumer.get_auth_portal = old_get_auth_portal

    def test_continue_authentication_calls_get_twitter_id_and_update_profile_on_success(self):
        "woooooo long function names"
        mock_http = RANDOMSTR()
        class MockWaiter(object):
            expected_methods = [{}, 'account/verify_credentials.json', mock_http]
            def __div__(mock, rhs):
                cmp = mock.expected_methods.pop()
                self.assertEqual(cmp, rhs)
                return mock 

        random_request_token = RANDOM()
        random_oauth_token = RANDOM()
        random_access_token = RANDOM()

        random_user = RANDOMSTR()
        class MockTwitterIdWithUser(object):
            user = random_user 
        fake_twitter_id = MockTwitterIdWithUser()

        self.mox.StubOutWithMock(TwitterConsumer, 'get_auth_portal')
        mock_consumer_class = TwitterConsumer
        mock_consumer = self.mox.CreateMock(TwitterConsumer)
        mock_consumer_class.get_auth_portal().AndReturn(mock_consumer)
        mock_consumer.get_access_token_from_twitter(random_request_token, random_oauth_token).AndReturn(random_access_token)
        mock_consumer.get_client(random_access_token).AndReturn(mock_http)

        mock_waiter_instance = MockWaiter()
        tp = TwitterAuthBackend(mock_consumer_class)
        self.mox.StubOutWithMock(tp, 'get_twitter_id')
        self.mox.StubOutWithMock(tp, 'update_twitter_profile')
        
        tp.get_twitter_id(mock_consumer, random_access_token, mock_waiter_instance).AndReturn(fake_twitter_id)
        tp.update_twitter_profile(fake_twitter_id, mock_waiter_instance)
        self.mox.ReplayAll()
        result = tp.continue_authentication(random_request_token, random_oauth_token, mock_waiter_instance)
        self.assertEqual(result, random_user)
        self.mox.VerifyAll()

    def test_get_twitter_id_delegates_to_register_new_user_on_nonexistant_id(self):
        mock_twitter_manager = self.mox.CreateMock(TwitterIdentification.objects)
        mock_twitter_manager.model = TwitterIdentification
        tb = TwitterAuthBackend(twitter_manager=mock_twitter_manager)
        random_consumer = RANDOM()
        random_access_token = RANDOM()
        random_credentials = { 'id': RANDOM() }
        random_result = RANDOM()

        mock_twitter_manager.get(consumer=random_consumer, uid=random_credentials['id']).AndRaise(TwitterIdentification.DoesNotExist)
        mock_twitter_manager.register_new_user(random_consumer, random_access_token, random_credentials).AndReturn(random_result)

        self.mox.ReplayAll()
        result = tb.get_twitter_id(random_consumer, random_access_token, random_credentials)
        self.assertEqual(result, random_result)
        self.mox.VerifyAll()

    def test_get_twitter_id_updates_twitter_id_on_found(self):
        random_uid = RANDOMSTR()
        tid = TwitterIdentification.objects.create(
            uid=random_uid,
            key=RANDOMSTR(),
            secret=RANDOMSTR(),
            user=User.objects.create(
                username=RANDOMSTR(),
            ),
            consumer=TwitterConsumer.objects.create(
                key=RANDOMSTR(),
                secret=RANDOMSTR(),
                auth_portal=Site.objects.create(
                    name=RANDOMSTR(),
                    domain='domain.com',
                )
            )
        )
        new_random_secret = RANDOMSTR()
        new_random_key = RANDOMSTR()
        random_access_token = oauth2.Token(new_random_key, new_random_secret)
        credentials = { 'id': random_uid }
        tb = TwitterAuthBackend()
        results = tb.get_twitter_id(tid.consumer, random_access_token, credentials)
        self.assertEqual(results.pk, tid.pk)
        self.assertEqual(results.key, new_random_key)
        self.assertEqual(results.secret, new_random_secret)

    def test_update_twitter_profile_updates_raw_data_on_found(self):
        random_uid = RANDOMSTR()
        tid = TwitterIdentification.objects.create(
            uid=random_uid,
            key=RANDOMSTR(),
            secret=RANDOMSTR(),
            user=User.objects.create(
                username=RANDOMSTR(),
            ),
            consumer=TwitterConsumer.objects.create(
                key=RANDOMSTR(),
                secret=RANDOMSTR(),
                auth_portal=Site.objects.create(
                    name=RANDOMSTR(),
                    domain='domain.com',
                )
            )
        )
        tprof = TwitterProfile.objects.create(
                    twitter_identification=tid,
                    raw_data=""
        )
        random_key = RANDOMSTR()
        random_credentials = { 'id':random_uid, random_key:RANDOM() }
        tb = TwitterAuthBackend()
        tb.update_twitter_profile(tid, random_credentials)
        self.assertEqual(tid.twitter_profile.pk, tprof.pk)
        self.assertEqual(getattr(tid.twitter_profile.data, random_key), random_credentials[random_key])

    def test_update_twitter_profile_creates_profile_if_none_exists(self):
        random_uid = RANDOMSTR()
        tid = TwitterIdentification.objects.create(
            uid=random_uid,
            key=RANDOMSTR(),
            secret=RANDOMSTR(),
            user=User.objects.create(
                username=RANDOMSTR(),
            ),
            consumer=TwitterConsumer.objects.create(
                key=RANDOMSTR(),
                secret=RANDOMSTR(),
                auth_portal=Site.objects.create(
                    name=RANDOMSTR(),
                    domain='domain.com',
                )
            )
        )
        random_key = RANDOMSTR()
        random_credentials = { 'id':random_uid, random_key:RANDOM() }
        tb = TwitterAuthBackend()
        tb.update_twitter_profile(tid, random_credentials)
        profile = tid.twitter_profile
        self.assertEqual(getattr(profile.data, random_key), random_credentials[random_key])


