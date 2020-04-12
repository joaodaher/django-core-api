from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth.models import User

from django_core_api.tests import BaseApiTest
from test_app import models


class BaseAdminTest(BaseApiTest):
    def setUp(self):
        self.username = "admin_test"
        self.email = 'admin@test.com'
        self.plain_password = 'abc@123'
        hashing = 'pbkdf2_sha256$100000'
        self.password = f'{hashing}$YaRnm7qeEoxM$6fZjStj2ebFCaP9h/3PV9RpSPZwAwKEVs2lcwtmXbvA='

    def login(self, staff=True):
        User.objects.create_user(
            id=42,
            username=self.email,
            password=self.plain_password,
            is_staff=staff,
            is_superuser=staff,
        )
        self.client.login(username=self.email, password=self.plain_password)


class TestAdminPanel(BaseAdminTest):
    def test_not_staff(self):
        self.login(staff=False)

        response = self.client.get('/admin/')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/admin/login/?next=/admin/', response.url)

    def test_home(self):
        self.login()

        response = self.client.get('/admin/')
        self.assertEqual(200, response.status_code)
        self.assertIn("<!DOCTYPE html", response.content.decode())

    def test_language(self):
        self.login()

        response = self.client.get('/admin/')
        self.assertEqual(200, response.status_code)
        self.assertIn("Administração do Site", response.content.decode())


class TestWizardAdmin(BaseAdminTest):
    def test_list_items(self):
        self.login(staff=True)

        wizard_a = models.Wizard.objects.create(
            name="Harry Potter",
        )
        wizard_b = models.Wizard.objects.create(
            name="Hermione Granger",
        )

        response = self.client.get('/admin/test_app/wizard/')
        self.assertEqual(200, response.status_code)

        expected = f'/admin/test_app/wizard/{wizard_a.pk}/change/'
        self.assertIn(expected, response.content.decode())

        expected = f'/admin/test_app/wizard/{wizard_b.pk}/change/'
        self.assertIn(expected, response.content.decode())

    def test_add_item(self):
        self.login(staff=True)

        data = {
            'name': "Harry Potter",
        }
        response = self.client.post('/admin/test_app/wizard/add/', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/admin/test_app/wizard/', response.url)

    def test_add_fail_item(self):
        self.login(staff=True)

        data = {
            'name': "Voldemort",
        }

        response = self.client.post(
            '/admin/test_app/wizard/add/',
            data=data,
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual('/admin/test_app/wizard/add/', response.url)

        self.assertFalse(models.Wizard.objects.exists())

        response = self.client.get(response.url)
        expected = 'YOU-KNOW-WHO'
        self.assertIn(expected, response.content.decode())

    def test_edit_item(self):
        self.login(staff=True)

        wizard = models.Wizard.objects.create(
            name="Parry Hotter",
        )

        data = {
            'name': "Harry Potter",
            'is_half_blood': True,
        }
        response = self.client.post(f'/admin/test_app/wizard/{wizard.pk}/change/', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/admin/test_app/wizard/', response.url)

        [wizard] = models.Wizard.objects.all()
        self.assertEqual("Harry Potter", wizard.name)
        self.assertEqual(True, wizard.is_half_blood)

    def test_edit_fail_item(self):
        self.login(staff=True)

        wizard = models.Wizard.objects.create(
            name="That Bald Guy",
        )

        data = {
            'name': "Voldemort",
            'is_half_blood': False,
        }
        response = self.client.post(f'/admin/test_app/wizard/{wizard.pk}/change/', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/admin/test_app/wizard/{wizard.pk}/change/', response.url)

        [wizard] = models.Wizard.objects.all()
        self.assertEqual("That Bald Guy", wizard.name)

        response = self.client.get(response.url)
        expected = 'YOU-KNOW-WHO'
        self.assertIn(expected, response.content.decode())

    def test_delete_item(self):
        self.login(staff=True)

        wizard = models.Wizard.objects.create(
            name="Snape",
        )

        data = {
            'post': "yes",
        }
        response = self.client.post(f'/admin/test_app/wizard/{wizard.pk}/delete/', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/admin/test_app/wizard/', response.url)

        self.assertFalse(models.Wizard.objects.exists())

    def test_delete_fail_item(self):
        self.login(staff=True)

        wizard = models.Wizard.objects.create(
            name="Harry Potter",
        )

        data = {
            'post': "yes",
        }

        url = f'/admin/test_app/wizard/{wizard.pk}/delete/'
        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual(url, response.url)

        self.assertTrue(models.Wizard.objects.exists())

        response = self.client.get(response.url)
        expected = 'Harry can never die'
        self.assertIn(expected, response.content.decode())

    def test_admin_timezone(self):
        self.login(staff=True)

        data = {
            'name': "Harry Potter",
            'received_letter_at_0': "1990-07-19",
            'received_letter_at_1': "07:30",
        }
        response = self.client.post('/admin/test_app/wizard/add/', data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/admin/test_app/wizard/', response.url)

        [wizard] = models.Wizard.objects.all()

        saved_date = pytz.timezone(settings.ADMIN_TIME_ZONE).localize(datetime(1990, 7, 19, 7, 30))
        expected_date = saved_date.astimezone(pytz.utc)
        self.assertEqual(expected_date, wizard.received_letter_at)
