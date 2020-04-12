import logging
from importlib import import_module

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_core_api.celery import app

logger = logging.getLogger(__name__)


class HealthCheck(APIView):
    SUCCESS = 'OK'
    ERROR = 'ERROR'

    def get(self, request):
        all_messages = []

        database_status = {}
        for name in connections:
            db_conn = connections[name]
            message = self._check_db(db_conn)
            database_status[db_conn.settings_dict.get('NAME', name)] = message

            all_messages.append(message)

        cache_status = self._check_cache()
        all_messages.append(cache_status)

        celery_status = self._check_celery()
        all_messages.extend(
            list(celery_status.values())
            if isinstance(celery_status, dict)
            else celery_status
        )

        data = {
            'databases': database_status,
            'cache': cache_status,
            'celery': celery_status,
        }

        custom_checks = getattr(settings, 'HEALTHCHECKS', {})
        for name, module_path in custom_checks.items():
            message = self._check_custom(module_path)
            all_messages.append(message)
            data[name] = message

        errored = any(self.ERROR in message for message in all_messages)
        r_status = status.HTTP_200_OK if not errored else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(
            data=data,
            status=r_status,
        )

    def _check_db(self, db_conn):
        try:
            db_conn.cursor()
            message = self.SUCCESS
        except OperationalError as e:
            message = '{}: {}'.format(self.ERROR, str(e))
            logger.error(f'[HEALTHCHECK] Database {repr(e)}')
        return message

    def _check_cache(self):
        if settings.CACHES['default']['BACKEND'] == 'django.core.cache.backends.dummy.DummyCache':
            return 'NA'

        key = 'HEALTHCHECK'
        value = now().isoformat()
        try:
            cache.set(key, value)
            if not cache.get(key) == value:
                raise Exception("Cached value does match as expected")
            message = self.SUCCESS
        except Exception as e:  # pylint: disable=W0703
            message = '{}: {}'.format(self.ERROR, str(e))
            logger.error(f'[HEALTHCHECK] Cache {repr(e)}')
        return message

    def _check_celery(self):
        if getattr(app.conf, 'broker_backend', None) == 'memory':
            return 'NA'

        message = {}

        try:
            workers = app.control.ping()[0]
            for name, worker_status in workers.items():
                if 'ok' not in worker_status:
                    message = '{}: Worker {} failed with {}'.format(self.ERROR, name, worker_status)
                    return message
                else:
                    message[name] = self.SUCCESS
        except IndexError:
            message = '{}: but no active workers'.format(self.SUCCESS)
        except Exception as e:  # pylint: disable=W0703
            message = '{}: {}'.format(self.ERROR, str(e))
            logger.error(f'[HEALTHCHECK] Celery {repr(e)}')
        return message

    def _check_custom(self, path):
        parts = path.split('.')
        module = import_module('.'.join(parts[:-1]))
        method = getattr(module, parts[-1])

        try:
            response = method()
            message = f'{self.SUCCESS}: {response}' if response else self.SUCCESS
        except Exception as e:  # pylint: disable=W0703
            message = f'{self.ERROR}: {e}'
            logger.error(f'[HEALTHCHECK] Custom {repr(e)}')
        return message
