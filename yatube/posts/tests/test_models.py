from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_model__post_have_correct_object_names(self):
        """Проверяем, что у модели поста корректно работает __str__."""
        post = PostModelTest.post
        expected_models_str = post.text[:settings.LENGHT_STR_METHOD]
        self.assertEqual(expected_models_str, str(post))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'title': 'название поста',
            'text': 'текст поста',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'title': 'введите название поста',
            'text': 'введите текст поста',
            'author': 'выберете автора',
            'group': 'выберете группу',
            'image': '',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model__group_have_correct_object_names(self):
        """Проверяем, что у модели группы корректно работает __str__."""
        group = GroupModelTest.group
        expected_models_str = group.title
        self.assertEqual(expected_models_str, str(group))

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'название группы',
            'slug': 'адрес группы',
            'description': 'описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_text = {
            'title': 'введите название группы',
            'slug': ('Введите уникальный адрес группы.'
                     'Используйте только латиницу, цифры,'
                     'дефисы и знаки подчёркивания'),
            'description': 'введите описание группы',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )
