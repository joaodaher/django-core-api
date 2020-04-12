import importlib
from unittest.mock import patch, Mock

from django_core_api import tasks
from django_core_api.tests import BaseApiTest


class RabbitMQTestMixin:
    def build_message_obj(self, exchange, routing_key, headers, properties):
        return Mock(
            delivery_info=dict(
                exchange=exchange,
                routing_key=routing_key,
            ),
            headers=headers,
            properties=Mock(**properties),
        )

    def patch_rabbitmq(self, url):
        return self.settings(RABBITMQ_URL=url)

    def _load_celery(self):
        from django_core_api import celery  # pylint: disable=import-outside-toplevel
        importlib.reload(celery)
        return celery.app.conf


class TestBaseTask(RabbitMQTestMixin, BaseApiTest):
    def test_task_fails(self):
        class LoserTask(tasks.BaseTask):
            def run(self, *args, **kwargs):
                raise ValueError('I failed you sir. - Alfred')

        my_task = LoserTask()
        with self.assertRaises(ValueError):
            my_task.delay()


class TestCelerySetup(RabbitMQTestMixin, BaseApiTest):
    def test_default_config(self):
        env_var = {}
        with self.patch_env(**env_var):
            conf = self._load_celery()
            self.assertEqual('memory', conf.broker_backend)
            self.assertTrue(conf.task_always_eager)

    def test_result_backend_not_set(self):
        env_var = {
            'RABBITMQ_URL': 'amqp://rabbit.test',
            'ENABLE_CELERY_RESULTS': '1',
        }
        with self.patch_env(**env_var):
            with self.patch_rabbitmq('amqp://rabbit.test'):
                with self.assertRaises(AttributeError):
                    self._load_celery()

    def test_result_backend_set(self):
        env_var = {
            'RABBITMQ_URL': 'amqp://rabbit.test',
            'ENABLE_CELERY_RESULTS': '1',
            'REDIS_URL': 'redis://elasticache.test',
        }
        with self.patch_env(**env_var):
            with self.patch_rabbitmq('amqp://rabbit.test'):
                conf = self._load_celery()
                self.assertEqual('amqp://rabbit.test/django_core_api', conf.broker_url)
                self.assertEqual('redis://elasticache.test', conf.result_backend)

    def test_broker_default(self):
        env_var = {
            'RABBITMQ_URL': 'amqp://rabbit.test',
        }
        with self.patch_env(**env_var):
            with self.patch_rabbitmq('amqp://rabbit.test'):
                conf = self._load_celery()
                self.assertIsNone(conf.result_backend)
                self.assertEqual('amqp://rabbit.test/django_core_api', conf.broker_url)


class TestBasePeriodicTask(RabbitMQTestMixin, BaseApiTest):
    def test_task_fails(self):
        class LoserPeriodicTask(tasks.BasePeriodicTask):
            run_every = 5

            def run(self, *args, **kwargs):
                raise ValueError('I failed you sir. - Alfred')

        my_task = LoserPeriodicTask()
        with self.assertRaises(ValueError):
            my_task.delay()
