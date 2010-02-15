from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db import models
from waiter.apis.twitter import TwitterMenu
from .managers import TwitterIdentificationManager
import oauth2
import urllib
import waiter

class TwitterConsumer(models.Model):
    """
        Associates many sites with a single consumer and auth portal site.
        *every consumer has one and only one auth_portal.*
    """
    sites = models.ManyToManyField(Site, related_name='twitter_consumers')
    auth_portal = models.OneToOneField(Site, related_name='twitter_auth_portal')
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)

    @classmethod
    def get_auth_portal(cls, manager=Site.objects):
        return manager.get_current().twitter_auth_portal

    @classmethod
    def get_current_consumer(cls, manager=Site.objects):
        try:
            return manager.get_current().twitter_consumers.all()[0]
        except:
            raise cls.DoesNotExist
    def get_current_site(self, manager=Site.objects):
        return manager.get_current()

    def get_oauth_consumer(self):
        return oauth2.Consumer(self.key, self.secret)

    def set_oauth_consumer(self, consumer):
        self.key, self.secret = consumer.key, consumer.secret
        return self.get_oauth_consumer()

    oauth_consumer = property(get_oauth_consumer, set_oauth_consumer)

    def get_request_token_from_twitter(self, http=None, api=None):
        bus_boy = waiter.Waiter(consumer=waiter.Consumer(), menu_class=TwitterMenu) if api is None else api 
        http = self.get_client() if http is None else http
        body = bus_boy/http/'https://twitter.com/oauth/request_token'/{
        }
        return oauth2.Token.from_string(body)

    def get_access_token_from_twitter(self, request_token, oauth_token_string, http=None, api=None):
        bus_boy = waiter.Waiter(method='POST', consumer=waiter.Consumer(), menu_class=TwitterMenu) if api is None else api
        http = self.get_client(request_token) if http is None else http
        body = bus_boy/http/'https://twitter.com/oauth/access_token'/{
            'oauth_token':oauth_token_string,
        }
        return oauth2.Token.from_string(body)

    def get_client(self, token=None):
        return oauth2.Client(self.oauth_consumer, token)

class TwitterIdentification(models.Model):
    user = models.OneToOneField(User, related_name='twitter_auth')
    consumer = models.ForeignKey(TwitterConsumer)
    uid = models.CharField(max_length=255)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)

    objects = TwitterIdentificationManager(User.objects)
    def get_oauth_token(self):
        if getattr(self, '_oauth_token', None) is None:
            self._oauth_token = oauth2.Token(self.key, self.secret)
        return self._oauth_token 

    def set_oauth_token(self, token):
        self.key, self.secret = token.key, token.secret
        if getattr(self, '_oauth_token', None) is not None:
            del self._oauth_token

    oauth_token = property(get_oauth_token, set_oauth_token)

    def get_client(self):
        return self.consumer.get_client(self.oauth_token)

class TwitterProfile(models.Model):
    twitter_identification = models.OneToOneField(TwitterIdentification, related_name='twitter_profile')
    raw_data = models.TextField()
    _unpacked_data = None

    def unpack_data(self):
        return type('TwitterProfileProxy', (), simplejson.loads(self.raw_data))()

    def pack_data(self):
        dict_to_pack = {}
        [dict_to_pack.update({key:getattr(self.data, key)}) for key in dir(self.data) if not key.startswith('__')]
        return simplejson.dumps(dict_to_pack)

    @property
    def data(self):
        self._unpacked_data = self._unpacked_data if self._unpacked_data else self.unpack_data()
        return self._unpacked_data
