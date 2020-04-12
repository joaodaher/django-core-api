from unittest.mock import patch

from django.db import OperationalError

from django_core_api.tests import BaseApiTest


def _custom_healthcheck_ok():
    return 'OK'


def _custom_healthcheck_error():
    raise Exception('potato')


class TestHealthcheckView(BaseApiTest):
    url = '/healthcheck'

    def _enable_celery(self, **kwargs):
        return patch('django_core_api.views.healthcheck_views.app')

    def _mock_celery_ping(self, **kwargs):
        if not kwargs:
            kwargs = {
                'return_value': [
                    {
                        'worker_a': 'everything is ok',
                    },
                ]
            }
        return patch('django_core_api.views.healthcheck_views.app.control.ping', **kwargs)

    def _mock_custom_healthcheck(self, error=False):
        module = '_custom_healthcheck_ok' if not error else '_custom_healthcheck_error'
        return self.settings(
            HEALTHCHECKS={
                'some-custom': f'test_app.tests.tests_views.tests_healthcheck_views.{module}'
            }
        )

    def test_healthcheck_complete_success(self):
        with self.real_cache(), self._enable_celery(), self._mock_celery_ping(), \
             self._mock_custom_healthcheck():
            response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_healthcheck_default_success(self):
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_healthcheck_success_celery_no_worker(self):
        with self._enable_celery(), self._mock_celery_ping(return_value=[]):
            response = self.client.get(self.url)

            self.assertEqual(200, response.status_code)
            self.assertIn('no active workers', response.data['celery'])

    def test_healthcheck_fail_custom(self):
        with self._mock_custom_healthcheck(error=True):
            response = self.client.get(self.url)

            self.assertEqual(503, response.status_code)
            self.assertIn('ERROR', response.data['some-custom'])

    def test_healthcheck_fail_cache(self):
        with self.real_cache():
            with patch(
                    'django_core_api.views.healthcheck_views.cache.set',
                    side_effect=Exception('potato'),
            ):
                response = self.client.get(self.url)

                self.assertEqual(503, response.status_code)
                self.assertIn('potato', response.data['cache'])

    def test_healthcheck_fail_db(self):
        error = OperationalError('potato')
        with patch('django.db.backends.postgresql.base.DatabaseWrapper.cursor', side_effect=error):
            response = self.client.get(self.url)

            self.assertEqual(503, response.status_code)
            self.assertIn('potato', response.data['databases']['test_django_core_api'])
