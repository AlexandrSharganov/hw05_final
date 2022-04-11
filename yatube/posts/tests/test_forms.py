import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
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
        cls.test_another_one_group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-another-one-group',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            author=cls.test_author,
            group=cls.test_group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.test_author)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_create_post_authorized_client(self):
        """Создание поста авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст нового поста',
            'group': self.test_group.pk,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст нового поста',
                author=self.user,
                group=self.test_group,
                image='posts/small.gif',
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_create_post_guest_client(self):
        """Создание поста неавторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст свежего поста',
            'group': self.test_group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse('users:login')
                             + '?next=/create/')

    def test_edit_post_by_author(self):
        """Авторизованный пользователь пытается отредактировать свой пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовое редактирование поста автором',
            'group': self.test_group.pk
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовое редактирование поста автором'
            ).filter(
                author=self.test_author
            ).filter(
                group=self.test_group
            ).filter(
                pub_date=self.test_post.pub_date
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.test_post.pk}))

    def test_edit_post_not_author(self):
        """Авторизованный пользователь пытается отредактировать чужой пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовое редактирование формы',
            'group': self.test_group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=self.test_post.text
            ).filter(
                author=self.test_post.author
            ).filter(
                group=self.test_post.group
            ).filter(
                pub_date=self.test_post.pub_date
            ).exists(),
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.test_post.author.username}))

    def test_edit_post_by_guest_client(self):
        """Неавторизованный пользователь пытается отредактировать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': ('Тестовое редактирование поста'
                     'неавторизованным пользователем'),
            'group': self.test_group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        next_adress = reverse('posts:post_edit',
                              kwargs={'post_id': self.test_post.pk})
        self.assertRedirects(response, reverse('users:login')
                             + f'?next={next_adress}')

    def test_create_post_authorized_client_without_group(self):
        """Создание поста без группы авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст нового поста',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст нового поста',
                author=self.user,
                group=None,
            ).exists()
        )

    def test_edit_post_by_author_change_group(self):
        """Авторизованный пользователь пытается
        отредактировать группу своего поста.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовое редактирование поста автором',
            'group': self.test_another_one_group.pk
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовое редактирование поста автором'
            ).filter(
                author=self.test_author,
                group=self.test_another_one_group,
                pub_date=self.test_post.pub_date,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.test_post.pk}))

    def test_create_comment_authorized_client(self):
        """Создание комментария авторизованным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.test_post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст комментария',
                author=self.user,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.test_post.pk}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_create_comment_guest_client(self):
        """Создание комментария неавторизованным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.test_post.pk},
            ),
            data=form_data,
            follow=True
        )
        next_adress = reverse('posts:add_comment',
                              kwargs={'post_id': self.test_post.pk})
        self.assertRedirects(response, reverse('users:login')
                             + f'?next={next_adress}')
        self.assertEqual(Comment.objects.count(), comments_count)
