from django_core_api.tasks import BaseTask


class NotifyMinisterOfMagicTask(BaseTask):
    def run(self, *args, **kwargs):
        print("Points to Griffindor!")
