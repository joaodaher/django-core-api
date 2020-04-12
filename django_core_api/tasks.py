import logging
import warnings

from celery.task import PeriodicTask, Task, task as _task

logger = logging.getLogger(__name__)


def task(*args, **kwargs):
    warnings.warn(f"@task is deprecated: use BaseTask class instead")
    kwargs['base'] = kwargs.get('base', BaseTask)
    return _task(*args, **kwargs)


class BaseTask(Task):
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = True
    expires = 60 * 60

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception(msg=f"{self.name} task failed", exc_info=exc)


class BasePeriodicTask(PeriodicTask):
    abstract = True
    autoretry_for = (Exception,)
    retry_backoff = True

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception(msg=f"{self.name} task failed", exc_info=exc)


class LogErrorTask(BaseTask):
    def run(self, request, exc, traceback):
        logger.exception(msg=f"Task {request.id} raised an error", exc_info=exc)
