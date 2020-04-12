import importlib
import logging

from django.db import models
from django.db.models import Max
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils.timezone import now
from ordered_model.models import OrderedModelBase

from django_core_api import exceptions, managers, signals
from django_core_api.serializers import as_dict

logger = logging.getLogger(__name__)


class ModelDiffMixin:
    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self._initial = self._dict

    @property
    def _diff(self):
        d1 = self._initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def _has_changed(self):
        return bool(self._diff)

    @property
    def _changed_fields(self):
        return self._diff.keys()

    def _get_field_diff(self, field_name):
        return self._diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self._initial = self._dict

    @property
    def _dict(self):
        return as_dict(model_to_dict(
            self,
            fields=[field.name for field in self._meta.fields],
        ))


class BaseModel(ModelDiffMixin, models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="última modificação"
    )

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ('-updated_at',)
        get_latest_by = 'updated_at'
        indexes = [
            models.Index(fields=['updated_at']),
        ]

    def admin_edit_url(self):
        return reverse(
            f'admin:{self._meta.app_label}_{self._meta.model_name}_change',
            args=[self.pk],
        )

    def save(self, *args, **kwargs):
        being_created = self.pk is None

        super(BaseModel, self).save(*args, **kwargs)

        if not being_created:
            return

        file_fields = [f for f in self._meta.get_fields() if isinstance(f, models.FileField)]

        if file_fields:
            changed = False
            for field in file_fields:
                file = getattr(self, field.name)
                if file:
                    old_file = file.name
                    new_file = file.field.generate_filename(self, old_file)

                    if new_file != old_file:
                        changed = True

                        file.storage.save(new_file, file)
                        file.name = new_file
                        file.close()
                        file.storage.delete(old_file)

            if changed:
                kwargs.pop('force_insert', None)
                super(BaseModel, self).save(*args, **kwargs)

    def __repr__(self):
        return f'<{self._meta.app_label}.{self.__class__.__name__} {self.pk}>'

    _SERIALIZER = None

    @classmethod
    def __serializer__(cls):
        try:
            module_name, klass_name = cls._SERIALIZER.rsplit('.', 1)
            return getattr(importlib.import_module(module_name), klass_name)
        except (AttributeError, ImportError):
            logger.info(f"Unable locate the auto-serializer {cls._SERIALIZER}")

    def to_dict(self):
        serializer = self.__serializer__()
        if serializer:
            return serializer(self).data
        else:
            return {
                'pk': self.pk,
            }


class AutoOrderedModelMixin(OrderedModelBase):
    order = models.PositiveIntegerField(
        db_index=True,
        default=None,
        null=True,
        blank=True,
        verbose_name="ordem",
    )
    order_field_name = 'order'

    def save(self, *args, **kwargs):
        if getattr(self, self.order_field_name) is None:
            c = self.get_ordering_queryset().aggregate(
                Max(self.order_field_name)
            ).get(self.order_field_name + '__max')
            new_order = 0 if c is None else c + 1
            setattr(self, self.order_field_name, new_order)
        super().save(*args, **kwargs)

        new_order = getattr(self, self.order_field_name, None)
        if not new_order:
            return

        clash = self.get_ordering_queryset().filter(
            **{self.order_field_name: new_order}
        ).exclude(pk=self.pk).first()
        if not clash:
            return

        setattr(clash, self.order_field_name, new_order + 1)
        clash.save()

    class Meta:
        abstract = True
        ordering = ('order',)


class InheritanceModel(BaseModel):
    type = models.CharField(
        max_length=100,
    )

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = []

    def save(self, *args, **kwargs):
        self.type = self.__class__.__name__.lower()
        return super().save(*args, **kwargs)


class SoftDeleteModel(BaseModel):
    deleted_at = models.DateTimeField(
        verbose_name="removido em",
        blank=True,
        null=True,
        default=None,
    )

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=['deleted_at']),
        ]

    objects = managers.SoftDeleteManager()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def save(self, *args, soft_deleting=False, **kwargs):
        if self.is_deleted and not soft_deleting:
            raise exceptions.UpdatingSoftDeletedException()
        return super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            signals.pre_soft_delete.send(
                sender=self.__class__,
                instance=self,
            )

            self.deleted_at = now()
            self.save(soft_deleting=True)

            signals.post_soft_delete.send(
                sender=self.__class__,
                instance=self,
            )

    def undelete(self):
        if self.is_deleted:
            signals.pre_undelete.send(
                sender=self.__class__,
                instance=self,
            )

            self.deleted_at = None
            self.save()

            signals.post_undelete.send(
                sender=self.__class__,
                instance=self,
            )
