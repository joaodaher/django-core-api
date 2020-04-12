import uuid

from django.conf import settings
from django.core.exceptions import ValidationError


def _build_storage():
    if settings.AWS_ACCESS_KEY_ID:
        from storages.backends.s3boto3 import S3Boto3Storage
        return S3Boto3Storage(location=settings.AWS_LOCATION + 'media')


MediaRootStorage = _build_storage


class BaseDataStoragePath:
    @classmethod
    def _build_kwargs(cls, upload_to):
        return {
            'upload_to': upload_to,
        }

    @classmethod
    def rename(cls, filename, new_name, unique=True):
        parts = filename.split('.')
        if len(parts) == 1:
            raise ValidationError("Filename must have and extension")

        extension = parts[-1]
        if unique:
            suffix = uuid.uuid4()
            new_name = f'{new_name}_{suffix}'
        return f'{new_name}.{extension}'

    @classmethod
    def _get_pk(cls, instance):
        if isinstance(instance, dict):
            pk = instance.get('id')
        else:
            pk = instance.pk

        if not pk:
            pk = uuid.uuid4()
        return str(pk)
