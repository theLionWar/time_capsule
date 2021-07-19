"""
Keys and secrets should be loaded of the  environment.
Put here only things that are shared between all production deployments.
"""

import logging
import environ
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

logging.debug("Settings loading: %s" % __file__)

# This will read only MISSING environment variables from a file
# We want to do this before loading any base settings as they
# may depend on environment
environ.Env.read_env(str(Path(__file__).parent / "production.env"),
                     DEBUG='False', ASSETS_DEBUG='False')

# noinspection PyUnresolvedReferences
from .base import *  # noqa

DEBUG = False

EMAIL_HOST_USER = 'arnon.cohen+time_capsule@mail.huji.ac.il'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # noqa
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGGING['handlers']['console']['formatter'] = 'verbose'  # noqa
LOGGING['handlers']['file'] = {  # noqa
    'class': 'logging.handlers.RotatingFileHandler',
    'formatter': 'verbose',
    'backupCount': 3,
    'maxBytes': 4194304,  # 4MB
    'level': 'DEBUG',
    'filename': (os.path.join(ROOT_DIR, 'logs', 'website.log')),  # noqa
}

LOGGING['handlers']['logzio']['token'] = os.environ.get('LOGZIO_KEY')  # noqa

LOGGING['root']['handlers'].append('file')  # noqa
LOGGING['root']['handlers'].append('logzio')  # noqa

log_file = Path(LOGGING['handlers']['file']['filename'])  # noqa
if not log_file.parent.exists():  # pragma: no cover
    logging.info("Creating log directory: {}".format(log_file.parent))
    Path(log_file).parent.mkdir(parents=True)


sentry_sdk.init(
    dsn=os.environ.get('SENTRY_URL'),  # noqa
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
