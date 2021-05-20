"""
Keys and secrets should be loaded of the environment.
Put here only things that are shared between all production deployments.
"""

import logging
import environ
from pathlib import Path

logging.debug("Settings loading: %s" % __file__)

# This will read only MISSING environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
environ.Env.read_env(str(Path(__file__).parent / "production.env"), DEBUG='False', ASSETS_DEBUG='False')

# noinspection PyUnresolvedReferences
from .base import *

DEBUG = False

LOGGING['handlers']['console']['formatter'] = 'verbose'
LOGGING['handlers']['file'] = {
    'class': 'logging.handlers.RotatingFileHandler',
    'formatter': 'verbose',
    'backupCount': 3,
    'maxBytes': 4194304,  # 4MB
    'level': 'DEBUG',
    'filename': (os.path.join(ROOT_DIR, 'logs', 'website.log')),
}
LOGGING['root']['handlers'].append('file')

log_file = Path(LOGGING['handlers']['file']['filename'])
if not log_file.parent.exists():  # pragma: no cover
    logging.info("Creating log directory: {}".format(log_file.parent))
    Path(log_file).parent.mkdir(parents=True)
