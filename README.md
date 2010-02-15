Introducing Bluebird
====================

So I wanted to try out my [Waiter](http://github.com/chrisdickinson/waiter) code
in a larger-scale project to see how it faired. About ten to twelve iced coffees,
later, I had Bluebird. It's a fairly simple app that adds Twitter OAuth
authentication to your Django app. The twist is -- and I'm not quite sure of how
relevant this will prove to be until Django 1.2 lands with multi-db support --
that this particular bird-themed authentication app is *heavily* dependent on
the `django.contrib.sites` module. There's no hard-coding of consumers here!

What does this mean for you? How does this even make sense? __WHY__?

Well, this is coded to address \(in theory\) situations like the following:

    <Site 1>    <Site 2>    <Authentication Portal>
        \           |       /
         \          |      /
        <OAuth Consumer for Sites 1 and 2>

So if you'd like a single sign-on for Sites one and two, bluebird might be the
app for you! Of course, it works just as well with a combined Site/Authportal
setup. 

How does it work
----------------
The (TwitterConsumer)[http://github.com/chrisdickinson/django-bluebird/bluebird/models.py]
object itself can be associated with many Sites -- these sites are end users of the 
Consumer; and registered with a single Site that serves as an `auth_portal`. To
configure a site as an auth_portal, its core settings.py should include a 
`IS_BLUEBIRD_AUTH_PORTAL = True` line. All sites using this app should include its
urls.py \(in the same location\), and add the app to INSTALLED_APPS.

In your templates, you can link to twitter as follows:

    <a href="{% url bluebird_initiate_login %}?next={% url relative_url_on_your_site %}">Twitter!</a>

When a user clicks on that -- joy of joys -- they'll go through this process

    site1.com/bluebird/initiate_login --302--> authsite.com/bluebird/portal_start_login --302--> twitter.com

and on the way back:

    twitter.com --302--> authsite.com/bluebird/login?oauth_token=blah --302--> site1.com/<whatever you set `next` to> 

Other Things
------------
When you authenticate a user with Twitter, you can get information about them in the 
following manner:

    user = User.objects.get(username='isntitvacant')
    user.twitter_auth                   # -> their authentication
    user.twitter_auth.get_client()      # -> returns a configured oauth2.Client ready for you to use
    user.twitter_auth.twitter_profile   # -> returns a cached profile object with jsonified data

    # but by doing the following:

    user.twitter_auth.data              # this will unpack the data
    print user.twitter_auth.data.screen_name    # prints the users screen_name

By default, when a user registers, it will attempt to create a user with an unusable password and
a username that matches their twitter screen_name. It will append underscores to their name
until a username is available.


This does open up some neat things, for example, updating a user's status is pretty easy:

    from waiter.apis.twitter import Twitter

    if hasattr(user, 'twitter_auth'):
        http = user.twitter_auth.get_client()
        waiter = Twitter()
        waiter/http/"statuses/update.json"/{
            'status':'I love eating food',
        }

Some Pitfalls
-------------
For the time being, this assumes that you've got multiple sites running a similar django installation
using a single database. I'm not exactly sure how common this is \(probably not very\). I'm 
imagining that when 1.2 hits this will be much more useful, as you could configure multiple sites
to use the same auth database, but otherwise keep seperate DB's.

Also, make sure you have a handler404 and a templates/404.html defined, or the tests will complain
at you loudly. Most everything is tested, though testing Waiter was a little difficult due to Mox
not supporting overriding `__div__`. 

INSTALLATION
============
* project/settings.py: 
** add 'bluebird' to INSTALLED_APPS
** add 'django.contrib.sites' to INSTALLED_APPS
** add 'south' to INSTALLED_APPS
** set your SITE_ID \(usually this will be SITE_ID = 1\)
** if this site will be used as an auth_portal, set IS_BLUEBIRD_AUTH_PORTAL = 1
** add `bluebird.backends.TwitterAuthBackend` to your AUTHENTICATION_BACKENDS
* project/urls.py
** add `('^bluebird/', include('bluebird.urls'))` to your urlpatterns
* now! `./manage.py syncdb && ./manage.py migrate`

REQUIREMENTS
============
* python >= 2.5
* mox -- testing
* simplegeo's oauth2 library
* waiter
* tested on django 1.1
* south -- migrations
