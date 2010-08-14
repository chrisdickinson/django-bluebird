from .models import TwitterConsumer, TwitterProfile, TwitterIdentification
from waiter.apis.twitter import Twitter, TwitterException
from django.contrib.auth.models import User
from django.utils import simplejson
from .views import TWITTER_REQUEST_TOKEN_KEY
import oauth2

class TwitterAuthBackend(object):
    def __init__(self, consumer_class=TwitterConsumer, twitter_manager=TwitterIdentification.objects, api_class=Twitter):
        self.twitter_manager = twitter_manager
        self.consumer_class = consumer_class
        self.api_class = api_class

    def authenticate(self, **credentials):
        try:
            request = credentials['twitter_request']
            oauth_token = request.GET['oauth_token']
            request_token = request.session[TWITTER_REQUEST_TOKEN_KEY]
        except KeyError:
            return None
        return self.continue_authentication(request_token, oauth_token)

    def continue_authentication(self, request_token, oauth_token, api_instance=None):
        consumer = self.consumer_class.get_auth_portal()
        access_token = consumer.get_access_token_from_twitter(request_token, oauth_token)
        twitter = self.api_class() if api_instance is None else api_instance
        http = consumer.get_client(access_token)
        try:
            credentials = twitter/http/'account/verify_credentials.json'/{
            }
            twitter_id = self.get_twitter_id(consumer, access_token, credentials)
            self.update_twitter_profile(twitter_id, credentials)
            return twitter_id.user
        except TwitterException:
            return None

    def get_twitter_id(self, consumer, access_token, credentials):
            try:
                twitter_id = self.twitter_manager.get(consumer=consumer, uid=credentials['id'])
                twitter_id.oauth_token = access_token
                twitter_id.save()
            except self.twitter_manager.model.DoesNotExist:
                twitter_id = self.twitter_manager.register_new_user(consumer, access_token, credentials)
            return twitter_id

    def update_twitter_profile(self, twitter_id, credentials):
        profile = None
        try:
            profile = twitter_id.twitter_profile
            profile.raw_data = simplejson.dumps(credentials) 
        except TwitterProfile.DoesNotExist:
            profile = TwitterProfile(twitter_identification=twitter_id, raw_data=simplejson.dumps(credentials))
        profile.save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)
