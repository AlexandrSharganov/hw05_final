from django.db import models
from django.contrib.auth import get_user_model

from core.models import PubDateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='название группы',
        help_text='введите название группы',)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='адрес группы',
        help_text=(
            'Введите уникальный адрес группы.'
            'Используйте только латиницу, цифры,'
            'дефисы и знаки подчёркивания'
        ),
    )
    description = models.TextField(
        verbose_name='описание',
        help_text='введите описание группы',)

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Post(PubDateModel):
    title = models.CharField(
        max_length=200,
        verbose_name='название поста',
        default='пост№',
        help_text='введите название поста')
    text = models.TextField(
        verbose_name='текст поста',
        help_text='введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
        help_text='выберете автора',)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='группа',
        help_text='выберете группу',)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ('-pub_date',)

    MAGIC_NUMBER = 15
    # Не знаю правильно ли я объявил константу и надо было ли?

    def __str__(self):
        return self.text[:self.MAGIC_NUMBER]


class Comment(PubDateModel):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
        help_text='выберете автора',)
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='Напишите комментарий')
    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ('-pub_date',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
