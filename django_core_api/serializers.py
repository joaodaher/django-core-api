from datetime import datetime

import json
import pytz
from django.db.models.fields.files import FieldFile
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ForeignKeyField(PrimaryKeyRelatedField):
    def __init__(self, queryset, write_only=True, **kwargs):
        super().__init__(queryset=queryset, write_only=write_only, **kwargs)

    def to_internal_value(self, data):
        return super().to_internal_value(data=data).pk


DATETIME_FORMAT = settings.REST_FRAMEWORK.get('DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%SZ')
DEFAULT_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


def as_str(value):
    if value is None:
        return None
    elif isinstance(value, datetime):
        value = assure_tz(value.astimezone(tz=DEFAULT_TIMEZONE))
        return value.strftime(DATETIME_FORMAT)
    return str(value)


def assure_tz(dt, tz=DEFAULT_TIMEZONE):
    if not dt:
        return dt
    if not dt.tzinfo:
        dt = tz.localize(dt)
    return dt


class CoreJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if o is None:
            return None
        elif isinstance(o, datetime):
            value = assure_tz(o.astimezone(tz=DEFAULT_TIMEZONE))
            return value.strftime(DATETIME_FORMAT)
        elif issubclass(o.__class__, FieldFile):
            return o.url if bool(o) else None
        else:
            return super().default(o)


def as_dict(items):
    serialized = json.dumps(items, cls=CoreJSONEncoder)
    return json.loads(serialized)
