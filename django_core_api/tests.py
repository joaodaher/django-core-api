import os
import re
from io import StringIO
from unittest.mock import patch

from django.core.cache import cache
from django.core.management import call_command
from rest_framework.test import APITransactionTestCase


class BaseApiTest(APITransactionTestCase):
    databases = '__all__'
    maxDiff = None
    multi_db = True

    def setUp(self):
        super().setUp()
        cache.clear()

    def real_cache(self):
        return self.settings(
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
                }
            }
        )

    def assertNoPendingMigration(self, app_name):
        out = StringIO()
        message = None
        try:
            call_command(
                'makemigrations',
                app_name,
                '--check',
                '--dry-run',
                interactive=False,
                stdout=out
            )
        except SystemExit:
            message = f'Missing migration. Run python manage.py makemigrations {app_name}'
        self.assertIn('No changes', out.getvalue(), msg=message)

    def assertUUIDFilePath(self, prefix, name, extension, pk, file):
        expected_path = r'^{prefix}/{pk}/{name}_{uuid}\.{extension}$'.format(
            prefix=prefix,
            pk=pk,
            name=name,
            extension=extension,
            uuid=r'[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}',
        )
        self.assertTrue(re.match(expected_path, str(file)))

    def patch_env(self, **kwargs):
        return patch.dict(os.environ, kwargs)
