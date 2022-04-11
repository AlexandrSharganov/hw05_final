from django.test import TestCase, Client

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls_dict = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def test_about_pages_urls(self):
        for url in self.urls_dict.keys():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )

    def test_about_pages_templates(self):
        for urls, templates in self.urls_dict.items():
            response = self.guest_client.get(urls)
            with self.subTest(urls=urls):
                self.assertTemplateUsed(
                    response, templates
                )
