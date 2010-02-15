from django.db import models

class TwitterIdentificationManager(models.Manager):
    def __init__(self, user_manager, *args, **kwargs):
        self.user_manager = user_manager
        return super(TwitterIdentificationManager, self).__init__(*args, **kwargs)

    def register_new_user(self, consumer, token, credentials):
        user = self.user_manager.create(
            username=self.create_username_from(credentials),
            password='!',
            is_active=True,
        )
        return self.create(
            user=user,
            consumer=consumer,
            uid=credentials['id'],
            key=token.key,
            secret=token.secret
        )

    def create_username_from(self, credentials):
        append_string = '_'
        i = 0
        get_appended_username = lambda x: x + (append_string*i)
        while self.user_manager.filter(username=get_appended_username(credentials['screen_name'])):
            i += 1
        return get_appended_username(credentials['screen_name'])

