from unittest.mock import patch

from django.core.cache import cache

from django_core_api.cache import CacheResponse
from django_core_api.tests import BaseApiTest
from test_app.tests.tests_base import HogwartsTestMixin


class TestCachedView(HogwartsTestMixin, BaseApiTest):
    url = '/teachers'

    def setUp(self):
        super().setUp()
        self.teachers = self._set_up_teachers()

    def test_cache_headers_endpoint(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('MISS', response['X-Cache'])

        cached_response = self.client.get(url)
        self.assertEqual(200, cached_response.status_code)
        self.assertEqual('HIT', cached_response['X-Cache'])

    def test_retrocompatible(self):
        url = self.url

        key_method = CacheResponse().calculate_key
        with patch('django_core_api.cache.CacheResponse.calculate_key', wraps=key_method) as calc:
            # Call the first time to get the response
            response = self.client.get(url)

            # Call again the key creation method to extract the cache key
            call_kwargs = calc.mock_calls[0][2]
            key = key_method(**call_kwargs)

        with self.real_cache():
            # In older DRF versions, the view cache is the whole response object
            cache.set(key, response)

            # Call again, hoping for a cache hit
            cached_response = self.client.get(url)
            self.assertEqual('HIT', cached_response['X-Cache'])

            self.assertEqual(response.json(), cached_response.json())

    def test_cache_by_using_content_type(self):
        url = self.url

        response_json_miss = self.client.get(url, HTTP_ACCEPT='application/json')
        self.assertEqual(200, response_json_miss.status_code)
        self.assertEqual('MISS', response_json_miss['X-Cache'])

        response_html_miss = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(200, response_html_miss.status_code)
        self.assertEqual('MISS', response_html_miss['X-Cache'])

        response_json_hit = self.client.get(url, HTTP_ACCEPT='application/json')
        self.assertEqual(200, response_json_hit.status_code)
        self.assertEqual('HIT', response_json_hit['X-Cache'])
        self.assertEqual(response_json_miss.content, response_json_hit.content)

        response_html_hit = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(200, response_html_hit.status_code)
        self.assertEqual('HIT', response_html_hit['X-Cache'])
