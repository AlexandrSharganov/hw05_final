from django.test import TestCase, Client

from posts.models import User
from http import HTTPStatus


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    urls_dict_guest_users = {
        '/auth/signup/': 'users/signup.html',
        '/auth/login/': 'users/login.html',
        '/auth/password_reset/': 'users/password_reset_form.html',
    }

    urls_dict_authorized_users = {
        '/auth/password_change/': 'users/password_change_form.html',
    }

    def test_users_urls_guest_users(self):
        for url, template in UsersURLTests.urls_dict_guest_users.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)

    def test_users_urls_authorized_users(self):
        for url, template in UsersURLTests.urls_dict_authorized_users.items():
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)
