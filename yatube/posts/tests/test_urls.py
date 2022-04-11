from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create(
            username='TestAuthor',
        )
        cls.test_group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            author=cls.test_author,
            group=cls.test_group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsURLTests.test_author)

        self.urls_dict_guest_users = {
            '/': 'posts/index.html',
            f'/group/{self.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.test_author.username}/': 'posts/profile.html',
            f'/posts/{self.test_post.pk}/': 'posts/post_detail.html',
        }

        self.urls_dict_authorized_users = {
            '/': 'posts/index.html',
            f'/group/{self.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.test_author.username}/': 'posts/profile.html',
            f'/posts/{self.test_post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

    def test_posts_urls_guest_users(self):
        """Проверка работы ссылок для неавторизованного пользователя."""
        for url, template in self.urls_dict_guest_users.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)
        response_create = self.guest_client.get('/create/', follow=True)
        response_edit = self.guest_client.get(
            f'/posts/{self.test_post.pk}/edit/', follow=True
        )
        response_follow = self.guest_client.get(
            f'/profile/{self.test_author.username}/follow/', follow=True
        )
        response_unfollow = self.guest_client.get(
            f'/profile/{self.test_author.username}/unfollow/', follow=True
        )
        self.assertRedirects(
            response_create, '/auth/login/?next=/create/'
        )
        self.assertRedirects(
            response_edit,
            f'/auth/login/?next=/posts/{self.test_post.pk}/edit/'
        )
        self.assertRedirects(
            response_follow,
            f'/auth/login/?next=/profile/{self.test_author.username}/follow/'
        )
        self.assertRedirects(
            response_unfollow,
            f'/auth/login/?next=/profile/{self.test_author.username}/unfollow/'
        )

    def test_posts_urls_authorized_users(self):
        """Проверка работы ссылок для авторизованного пользователя."""
        for url, template in self.urls_dict_authorized_users.items():
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template)
        response_follow = self.authorized_client.get(
            f'/profile/{self.test_author.username}/follow/', follow=True
        )
        self.assertRedirects(
            response_follow,
            f'/profile/{self.test_author.username}/'
        )
        response_unfollow = self.authorized_client.get(
            f'/profile/{self.test_author.username}/unfollow/', follow=True
        )
        self.assertRedirects(
            response_unfollow,
            f'/profile/{self.test_author.username}/'
        )

    def test_posts_urls_author(self):
        """Проверка работы ссылок для авторизованного автора."""
        response = self.authorized_author.get(
            f'/posts/{self.test_post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Проверка работы несуществующих страниц."""
        response_guest = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response_guest.status_code, HTTPStatus.NOT_FOUND)
