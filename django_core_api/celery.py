from celery import Celery

from envparse import env

from django_core_api import APP_NAME


app = Celery(APP_NAME)
app.conf.default_delivery_mode = 'transient'
app.conf.broker_pool_limit = env.int('BROKER_POOL_LIMIT', default=0)
app.conf.task_default_queue = f'celery'
app.conf.task_routes = {
}

RABBITMQ_URL = env.str('RABBITMQ_URL', default='')
if RABBITMQ_URL:
    app.conf.broker_url = f"{RABBITMQ_URL}/{APP_NAME}"

    if env.bool('ENABLE_CELERY_RESULTS', default=False):
        REDIS_URL = env.str('REDIS_URL', default='')
        if not REDIS_URL:
            raise AttributeError("REDIS_URL must be defined if ENABLE_CELERY_RESULTS is set")
        app.conf.result_backend = REDIS_URL
else:
    app.conf.broker_backend = 'memory'
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True


app.autodiscover_tasks()
