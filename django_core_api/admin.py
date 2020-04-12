import logging

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect


class ModelAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            return super().change_view(request, object_id, form_url, extra_context)
        except ValidationError as e:
            return self._handle_validation_error(request=request, error=e)

    def delete_view(self, request, object_id, extra_context=None):
        try:
            return super().delete_view(request, object_id, extra_context)
        except ValidationError as e:
            return self._handle_validation_error(request=request, error=e)

    def add_view(self, request, form_url='', extra_context=None):
        try:
            return super().add_view(request, form_url, extra_context)
        except ValidationError as e:
            return self._handle_validation_error(request=request, error=e)

    def _handle_validation_error(self, request, error):
        messages = []
        if getattr(error, 'error_list', None):
            for e in error.error_list:
                messages.extend(e.messages)
        elif getattr(error, 'error_dict', None):
            for key, value in error.error_dict.items():
                messages.append(f"[{key}] {value}")
        else:
            messages.append(error.message)
        message = '\n'.join(messages)

        self.message_user(request, message, level=logging.ERROR)
        return self._on_error_redirect(request=request)

    def _on_error_redirect(self, request):
        return HttpResponseRedirect(request.path)
