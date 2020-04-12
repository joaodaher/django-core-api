import importlib

from django.apps import AppConfig

from django_core_api.settings import UNSET


class BaseAppConfig(AppConfig):
    def ready(self):
        self._load_signals()
        self._load_tasks()
        self._load_model_serializers()

    def _load_signals(self):
        try:
            importlib.import_module(f"{self.name}.signals")
        except ImportError as e:
            if 'signals' not in str(e):
                raise

    def _load_tasks(self):
        try:
            importlib.import_module(f"{self.name}.tasks")
        except ImportError as e:
            if 'tasks' not in str(e):
                raise

    def _get_model_parent_attr(self, model, attr):
        from django_core_api.models import BaseModel  # pylint: disable=import-outside-toplevel
        for parent in model.__bases__:
            if issubclass(parent, BaseModel):
                return getattr(parent, attr, None)
        return None

    def _load_model_serializers(self):
        attr = '_SERIALIZER'
        for model in self.get_models():
            parent_name = self._get_model_parent_attr(model=model, attr=attr)
            name = getattr(model, attr, None)
            if name not in [UNSET, parent_name]:
                continue  # overwritten/custom serializer klass

            default_name = f'{self.name}.serializers.{model.__name__}Serializer'
            setattr(model, attr, default_name)


class CoreConfig(BaseAppConfig):
    name = 'django_core_api'
    verbose_name = "Django Core RESTFul API Framework"
