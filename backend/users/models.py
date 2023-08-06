from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .manage import UserManager

MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254


class CustomUser(AbstractUser):
    objects = UserManager()

    username = models.CharField(
        max_length=MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message='Некорректные символы, только буквы, цифры и @.+_-',
            )
        ],
        error_messages={
            'unique': 'Имя пользователя уже занято',
        },
        verbose_name='Никнейм пользователя',
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH, blank=True, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH, blank=True, verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Тот, на кого подписан',
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписка на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписаться на самого себя',
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
