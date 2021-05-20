# coding=utf-8
from __future__ import absolute_import

# When defaults are loaded assume a local development environment
# All other environments should explicitly choose a right settings
# IIRC - in prod/staging, in the web server that runs Django,
# we should explicitly load the settings file needed,
# for example in manage.py: os.environ.setdefault('DJANGO_SETTINGS_MODULE',
# 'time_capsule.settings.production')
from .local import *  # noqa
