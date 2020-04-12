from django.urls import path, include
from rest_framework.routers import DefaultRouter

from test_app import views

router = DefaultRouter(trailing_slash=False)

router.register(
    r'wizards',
    views.WizardViewSet,
    'wizard',
)

router.register(
    r'houses',
    views.HouseViewSet,
    'house',
)

router.register(
    r'teachers',
    views.TeacherViewSet,
    'teacher',
)

router.register(
    r'spells',
    views.SpellViewSet,
    'spell',
)

router.register(
    r'wizards/(?P<wizard_id>[^/.]+)/patronus',
    views.WizardPatronusViewSet,
    'wizard-to-patronus',
)

router.register(
    r'houses/(?P<house_id>[^/.]+)/wizards',
    views.HouseWizardsViewSet,
    'house-to-wizard',
)

router.register(
    r'spell-casts',
    views.SpellCastViewSet,
    'spell-cast',
)


urlpatterns = [
    path('', include('django_core_api.urls')),
] + router.urls
