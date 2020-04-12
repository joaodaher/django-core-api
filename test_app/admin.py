from django.contrib import admin

from django_core_api.admin import ModelAdmin
from test_app import models


@admin.register(models.Wizard)
class WizardAdmin(ModelAdmin):
    list_display = (
        'id',
        'name',
        'age',
    )
    list_filter = (
        'age',
        'is_half_blood',
    )
    search_fields = (
        'name',
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
    )
    fieldsets = [
        ('Informações', {
            'fields': (
                'id',
                'name',
                'created_at',
                'updated_at',
            )
        }),
        ('Mais Informações', {
            'fields': (
                'age',
                'is_half_blood',
                'received_letter_at',
            )
        }),
    ]
