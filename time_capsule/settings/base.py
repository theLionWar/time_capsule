"""
Django settings for time_capsule project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import environ
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = []

if 'ALLOWED_HOSTS' in os.environ:
    hosts = os.environ['ALLOWED_HOSTS'].split(" ")
    BASE_URL = "https://" + hosts[0]
    for host in hosts:
        host = host.strip()
        if host:
            ALLOWED_HOSTS.append(host)

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'playlist_creation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'playlist_creation.middleware.SocialAuthExceptionNotRaiseMiddleware',
]

ROOT_URLCONF = 'time_capsule.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.spotify.SpotifyOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'playlist_creation.services.create_playlist_in_target_social_pipeline',
)

SOCIAL_AUTH_SPOTIFY_SCOPE = ['playlist-modify-public']


WSGI_APPLICATION = 'time_capsule.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if "DATABASE_URL" in os.environ:  # pragma: no cover
    # Enable database config through environment
    DATABASES = {
        # Raises ImproperlyConfigured exception if DATABASE_URL not in
        # os.environ
        'default': env.db(),
    }

    # Make sure we use have all settings we need
    DATABASES['default']['TEST'] = {'NAME':
                                    os.environ.get("DATABASE_TEST_NAME", None)}
    DATABASES['default']['OPTIONS'] = {
        'options': '-c search_path=gis,public,pg_catalog',
        # 'sslmode': 'require',
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    # Setting this to True may disable preexisting loggers, for eg. Celery
    'disable_existing_loggers': False,
    'formatters': {
        'short': {
            'format': '%(asctime)s %(levelname)-7s %(thread)-5d %(message)s',
            'datefmt': '%H:%M:%S',
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)-7s %(thread)-5d %(name)s %(filename)s:%(lineno)s | %(funcName)s | %(message)s',  # noqa
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },

    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'short',
            'level': 'DEBUG',
        },
        'mail_admins': {
            'level': 'ERROR',
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        # 'sentry': {
        #     'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.  # noqa
        #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  # noqa
        #     'tags': {'custom-tag': 'x'},
        # },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },
        'django.security.DisallowedHost': {
            'handlers': [],
            'propagate': False,
        },
        'suds': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'factory.generate': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'factory.containers': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'raven': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        # 'sentry.errors': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = 'thank_you'
LOGIN_ERROR_URL = 'home'

SOCIAL_AUTH_SPOTIFY_KEY = env('SOCIAL_AUTH_SPOTIFY_KEY')
SOCIAL_AUTH_SPOTIFY_SECRET = env('SOCIAL_AUTH_SPOTIFY_SECRET')

LASTFM_API_KEY = env('LASTFM_API_KEY')
LASTFM_SHARED_SECRET = env('LASTFM_SHARED_SECRET')
