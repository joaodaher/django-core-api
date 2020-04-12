import os
from unittest.mock import patch

from django_core_api import parse_app_name
from django_core_api.tests import BaseApiTest


class TestParseAppName(BaseApiTest):
    def patch_warning(self):
        return patch('logging.Logger.warning')

    def patch_environ(self, env=None, tsuru_app_name=None, app_name=None, current_version=None):
        envs = {}
        if env:
            envs['ENV'] = env
        else:
            os.environ.pop('ENV', None)

        if tsuru_app_name:
            envs['TSURU_APPNAME'] = tsuru_app_name
        else:
            os.environ.pop('TSURU_APPNAME', None)

        if app_name:
            envs['APP_NAME'] = app_name
        else:
            os.environ.pop('APP_NAME', None)

        if current_version:
            envs['APP_CURRENT_VERSION'] = current_version
        else:
            os.environ.pop('APP_CURRENT_VERSION', None)

        return patch.dict(os.environ, envs)

    def test_detect_dir_name(self):
        with self.patch_environ():
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('django_core_api', app)
        self.assertEqual('dev', env)
        self.assertEqual(None, version)

    def test_parse_tsuru_name(self):
        with self.patch_environ(tsuru_app_name='potato-api-dev'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('potato_api', app)
        self.assertEqual('dev', env)
        self.assertEqual(None, version)

    def test_parse_app_name(self):
        with self.patch_environ(app_name='potato-api-dev'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('potato_api', app)
        self.assertEqual('dev', env)
        self.assertEqual(None, version)

    def test_parse_weird_env(self):
        with self.patch_environ(tsuru_app_name='potato-api-gergelim'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_called_once()

        self.assertEqual('potato_api', app)
        self.assertEqual('gergelim', env)
        self.assertEqual(None, version)

    def test_parse_very_long_name(self):
        with self.patch_environ(app_name='potato-or-tomato-api-prd'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('potato_or_tomato_api', app)
        self.assertEqual('prd', env)
        self.assertEqual(None, version)

    def test_app_version(self):
        with self.patch_environ(current_version='3.14', app_name='potato-api-prd'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('potato_api', app)
        self.assertEqual('prd', env)
        self.assertEqual('3.14', version)

    def test_explicit_env(self):
        with self.patch_environ(env='test'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_not_called()

        self.assertEqual('django_core_api', app)
        self.assertEqual('test', env)
        self.assertEqual(None, version)

    def test_explicit_env_but_app_name(self):
        with self.patch_environ(env='test', app_name='potato-api-prd'):
            with self.patch_warning() as warn:
                app, env, version = parse_app_name()

        warn.assert_called_once()

        self.assertEqual('potato_api', app)
        self.assertEqual('prd', env)
        self.assertEqual(None, version)
