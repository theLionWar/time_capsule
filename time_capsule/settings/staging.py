"""
These should mimic a production settings making minimal modifications to accommodate tests
"""

import logging
import environ
from pathlib import Path

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.debug("Settings loading: %s" % __file__)

# This will read missing environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
environ.Env.read_env(str(Path(__file__).parent / "staging.env"), DEBUG=False)

# noinspection PyUnresolvedReferences
from .base import *
