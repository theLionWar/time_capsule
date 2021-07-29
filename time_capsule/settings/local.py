import logging
import environ

logging.debug("Settings loading: %s" % __file__)

# This will read missing environment variables from a file
# We wan to do this before loading a base settings as they may
# depend on environment
environ.Env.read_env(DEBUG='True')

from .base import *  # noqa

ALLOWED_HOSTS += [  # noqa
    '127.0.0.1',
    'localhost',
    ]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SOCIAL_AUTH_SPOTIFY_KEY = '68946c4a10cc44b6ba7a650fa28ebf4b'
SOCIAL_AUTH_SPOTIFY_SECRET = env('SOCIAL_AUTH_SPOTIFY_SECRET')  # noqa

LASTFM_API_KEY = '7a7e0754c3ca603c221a61ca0ba03ef7'
LASTFM_SHARED_SECRET = env('LASTFM_SHARED_SECRET')  # noqa

TEST_SPOTIFY_USERNAME = env('TEST_SPOTIFY_USERNAME')  # noqa
TEST_SPOTIFY_PASSWORD = env('TEST_SPOTIFY_PASSWORD')  # noqa

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
