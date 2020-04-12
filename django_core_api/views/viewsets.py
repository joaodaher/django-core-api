import logging

from django.db.utils import IntegrityError
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import BaseCacheResponseMixin

from django_core_api.cache import cache_response, cache_key_constructor

logger = logging.getLogger(__name__)


class MultiSerializerMixin:
    serializer_detail_class = None
    queryset_detail = None

    serializer_create_class = None
    queryset_create = None

    serializer_update_class = None
    queryset_update = None

    def get_serializer_class(self):
        klass = None
        verb = self.request.method.lower()

        if verb == 'get' and self._is_request_to_detail_endpoint():
            klass = self.serializer_detail_class
        elif verb == 'post':
            klass = self.serializer_create_class
        elif verb == 'patch':
            klass = self.serializer_update_class or self.serializer_create_class

        if not klass:
            klass = super().get_serializer_class()
        return klass

    def get_queryset(self, *args, **kwargs):
        queryset = None
        verb = self.request.method.lower()

        if verb == 'get' and self._is_request_to_detail_endpoint():
            queryset = self.queryset_detail
        elif verb == 'post':
            queryset = self.queryset_create
        elif verb == 'patch':
            queryset = self.queryset_update or self.queryset_create

        if not queryset:
            queryset = super().get_queryset(*args, **kwargs)
        else:
            queryset = queryset.all()
        return queryset

    def _is_request_to_detail_endpoint(self):
        if hasattr(self, 'lookup_url_kwarg'):
            lookup = self.lookup_url_kwarg or self.lookup_field
        return lookup and lookup in self.kwargs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        detail_serializer_klass = self.serializer_detail_class or self.serializer_class
        data = detail_serializer_klass(obj).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        detail_serializer_klass = self.serializer_detail_class or self.serializer_class
        data = detail_serializer_klass(obj).data
        return Response(data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # identical override of parent method, but returns the object
        return serializer.save()

    def perform_update(self, serializer):
        # identical override of parent method, but returns the object
        return serializer.save()


class ModelViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            if 'duplicate key value violates unique' in str(e):
                message = f'Duplicate key constraint raised for {e}. ' \
                          'Try adding a UniqueTogetherValidator to the serializer'
                logger.error(message)
                raise ValidationError({'error': "Already exists"})
            raise e


class ReadOnlyModelViewSet(MultiSerializerMixin, viewsets.ReadOnlyModelViewSet):
    http_method_names = ['get', 'head', 'options']


class CacheResponseMixin(BaseCacheResponseMixin):
    @cache_response(key_func=cache_key_constructor)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(key_func=cache_key_constructor)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CachedModelViewSet(CacheResponseMixin, ModelViewSet):
    pass


class CachedReadOnlyModelViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pass
