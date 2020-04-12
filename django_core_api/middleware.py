import logging

import pytz
from django.conf import settings
from django.utils import translation, timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AdminLocaleURLMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin'):
            lang = getattr(settings, 'ADMIN_LANGUAGE_CODE', settings.LANGUAGE_CODE)
            request.LANG = request.LANGUAGE_CODE = lang

            lang = request.LANG
            tzname = getattr(settings, 'ADMIN_TIME_ZONE', settings.TIME_ZONE)
        else:
            tzname = getattr(settings, 'TIME_ZONE')
            lang = getattr(settings, 'LANGUAGE_CODE')

        translation.activate(lang)
        timezone.activate(pytz.timezone(tzname))
