# pylint: disable=W0614,C0413,W0401

import os

from envparse import env


# Paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Security
SECRET_KEY = env.str('SECRET_KEY', default='3.14159265359')


# Application
INSTALLED_APPS = [
    'django_core_api.apps.CoreConfig',

    'test_app.apps.SampleAppConfig',
]


from django_core_api.settings import *


ROOT_URLCONF = 'test_app.urls'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}
