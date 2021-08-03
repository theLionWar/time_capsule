# coding=utf-8
from __future__ import absolute_import
import os

# When defaults are loaded assume a local development environment
# All other environments should explicitly choose a right settings
# IIRC - in prod/staging, in the web server that runs Django,
# we should explicitly load the settings file needed,
# for example in manage.py: os.environ.setdefault('DJANGO_SETTINGS_MODULE',
# 'time_capsule.settings.production')

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'time_capsule.settings':
    try:
        from .local_settings import *  # noqa
    except ImportError:
        from .local import *  # noqa
