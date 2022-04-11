import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, User, Group, Comment, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
        cls.test_another_group = Group.objects.create(
            title='Тестовое название другой группы',
            slug='test-another-group',
            description='Другое Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.test_post = Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            author=cls.test_author,
            group=cls.test_group,
            image=cls.uploaded,
        )
        cls.test_comment = Comment.objects.create(
            post=cls.test_post,
            author=cls.test_author,
            text='Тестовый текст',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.test_author)
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.urls_dict_authorized_users = {
            reverse('posts:posts'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.test_group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.test_author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.test_post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.test_post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:follow_index',
            ): 'posts/follow.html',
            # '/unexisting_page/': 'core/404.html'
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.urls_dict_authorized_users.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Тест проверяет контекст при просмотре главной страницы."""
        response = self.authorized_client.get(reverse('posts:posts'))
        first_object_index = response.context['page_obj'][0]
        self.assertEqual(first_object_index, self.test_post)

    def test_group_page_show_correct_context(self):
        """Тест проверяет контекст при просмотре страницы группы."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.test_group.slug})
        )
        first_object_group = response.context['page_obj'][0]
        context_group = response.context['group']
        self.assertEqual(first_object_group, self.test_post)
        self.assertEqual(context_group, self.test_group)

    def test_profile_page_show_correct_context(self):
        """Тест проверяет контекст при просмотре страницы профиля."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.test_author.username})
        )
        first_object_profile = response.context['page_obj'][0]
        context_author = response.context['author']
        self.assertEqual(first_object_profile, self.test_post)
        self.assertEqual(context_author, self.test_author)

    def test_post_detail_show_correct_context(self):
        """Тест проверяет контекст при просмотре отдельного поста."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.test_post.pk})
        )
        post_detail = response.context['post']
        comments = response.context['comments'][0]
        self.assertEqual(post_detail, self.test_post)
        self.assertEqual(comments, self.test_comment)

    def test_create_post_show_correct_context(self):
        """Тест проверяет контекст формы при создании поста."""
        response = self.authorized_client.get(reverse(
            'posts:post_create',)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Тест проверяет контекст формы при редактировании поста."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.test_post.pk},)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, True)

    def test_another_group_page_dont_include_test_post(self):
        """Тест проверяет что пост не содержится в чужой группе."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.test_another_group.slug})
        )
        dict_object_group = response.context['page_obj']
        test_post = get_object_or_404(Post, pk=self.test_post.pk)
        self.assertNotIn(
            test_post,
            dict_object_group,
            'Запись попала в чужую группу!!!')

    def test_cash_work(self):
        """Проверяем кэширование на главной."""
        response = self.authorized_client.get(reverse('posts:posts'))
        first_object = response.content
        form_data = {
            'text': 'Test cache',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        Post.objects.get(text='Test cache').delete()
        response = self.authorized_client.get(reverse('posts:posts'))
        second_object = response.content
        self.assertEqual(first_object, second_object)

    def test_follow_page_show_correct_context(self):
        """Тест проверяет контекст при просмотре избранных авторов."""
        Follow.objects.create(
            user=self.user,
            author=self.test_author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object_follow = response.context['page_obj'][0]
        self.assertEqual(first_object_follow, self.test_post)

    def test_profile_follow(self):
        """Авторизованный пользователь добавляет подписку."""
        follow_count = Follow.objects.count()
        self.authorized_client.get('/profile/TestAuthor/follow/')
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.test_author,
            )
        )

    def test_new_post_in_follow_page(self):
        """Проверяем что новый пост появился в ленте у подписчика"""
        Follow.objects.create(
            user=self.user,
            author=self.test_author
        )
        form_data = {
            'text': 'Новый поста для подписчика',
            'group': self.test_group.pk,
        }
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        profile_page = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.test_author.username})
        )
        follow_page = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            profile_page.context['page_obj'][0],
            follow_page.context['page_obj'][0]
        )


class PaginatorViewsTest(TestCase):
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
        cls.test_post = []
        cls.AMOUNT_NEW_POSTS: int = 13
        cls.POSTS_PER_PAGE: int = 10
        for i in range(0, cls.AMOUNT_NEW_POSTS):
            cls.test_post.append(
                Post.objects.create(
                    title='Тестовый заголовок' + str(i),
                    text='Тестовый текст' + str(i),
                    author=cls.test_author,
                    group=cls.test_group,
                )
            )

    def test_first_page_index_group_profile(self):
        """Проверка работы первой страницы пагинатора."""
        dict_context_urls = {
            reverse('posts:posts'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.test_group.slug}): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.test_author.username}): 'page_obj',
        }
        for url, context in dict_context_urls.items():
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    len(response.context[context]),
                    self.POSTS_PER_PAGE
                )

    def test_second_page_index_group_profile(self):
        """Проверка работы второй страницы пагинатора."""
        dict_context_urls = {
            reverse('posts:posts') + '?page=2': 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.test_group.slug}) + '?page=2': 'page_obj',
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.test_author.username
                }
            ) + '?page=2': 'page_obj',
        }
        for url, context in dict_context_urls.items():
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    len(response.context[context]),
                    (self.AMOUNT_NEW_POSTS - self.POSTS_PER_PAGE)
                )
