from ..managers import TwitterIdentificationManager
from ..models import TwitterConsumer, TwitterIdentification
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.test import TestCase
import mox
import random
import oauth2

def RANDOM():
    return random.randint(1,100)

def RANDOMSTR(string='rand'):
    return string+str(RANDOM())

class TestOfTwitterIdentificationManager(TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_init_sets_manager(self):
        random_value = RANDOM()
        manager = TwitterIdentificationManager(random_value)
        self.assertEqual(random_value, manager.user_manager)

    def test_register_new_user_calls_usermanager(self):
        consumer = TwitterConsumer.objects.create(
                    auth_portal=Site.objects.create(
                        domain=RANDOMSTR(),
                        name=RANDOMSTR()
                    ),
                    key=RANDOMSTR(),
                    secret=RANDOMSTR(),
        ) 

        user_manager = self.mox.CreateMock(User.objects)
        fake_user = User.objects.create(
            username=RANDOMSTR()
        )

        fake_random_username = fake_user.username
        credentials = {
            'id':RANDOM(),
            'screen_name':fake_random_username,
        }
        user_manager.filter(**{
            'username':fake_random_username
        }).AndReturn(0)
        user_manager.create(**{
            'username':fake_random_username,
            'password':'!',
            'is_active':True
        }).AndReturn(fake_user)
        fake_token = oauth2.Token(RANDOMSTR(), RANDOMSTR())
        manager = TwitterIdentificationManager(user_manager)
        manager.model = TwitterIdentification
        self.mox.ReplayAll()
        new_fake_user = manager.register_new_user(consumer, fake_token, credentials) 
        self.assertEqual(new_fake_user.uid, credentials['id'])
        self.mox.VerifyAll()

    def test_create_username_from_returns_base_username_if_none_exists(self):
        credentials = {
            'screen_name':RANDOMSTR()
        }
        manager = TwitterIdentificationManager(User.objects)
        result = manager.create_username_from(credentials)
        self.assertEqual(credentials['screen_name'], result)

    def test_create_username_appends_underscores_until_unique_name(self):
        credentials = {
            'screen_name':RANDOMSTR(),
        }
        random_number_of_underscores = random.randint(1,39-len(credentials['screen_name']))
        for i in range(0, random_number_of_underscores):
            User.objects.create(
                username=credentials['screen_name']+('_'*i),
            )
        manager = TwitterIdentificationManager(User.objects)
        result = manager.create_username_from(credentials)
        self.assertEqual(len(credentials['screen_name'])+random_number_of_underscores, len(result))
