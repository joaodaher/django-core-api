from django_core_api import filters
from test_app import models


class TeacherFilterSet(filters.IncludeUnavailableFilterSet):
    id = filters.AnyOfFilter()

    class Meta:
        model = models.Teacher
        fields = [
            'id',
            'include_unavailable',
            'is_half_blood',
        ]
