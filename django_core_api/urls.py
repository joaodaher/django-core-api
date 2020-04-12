from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import models as auth_models
from django.urls import include, path
from django_celery_beat import models as celery_models

from django_core_api import views

admin.autodiscover()

try:
    admin.site.unregister(auth_models.User)
    admin.site.unregister(auth_models.Group)
except NotRegistered:
    pass

admin.site.unregister(celery_models.PeriodicTask)
admin.site.unregister(celery_models.SolarSchedule)
admin.site.unregister(celery_models.IntervalSchedule)
admin.site.unregister(celery_models.CrontabSchedule)

admin.site.site_header = settings.SITE_NAME

urlpatterns = [
    path(r'healthcheck', views.HealthCheck.as_view()),

    path('admin/', admin.site.urls),

    path('nested_admin/', include('nested_admin.urls')),
]
