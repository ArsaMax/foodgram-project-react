from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

MAX_LENGTH = 15


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    email = models.EmailField(
        'E-mail',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), ],
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:MAX_LENGTH]


class Subscription(models.Model):
    """Подписки пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчики',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_by',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created_at', )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='Repeat_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user[:MAX_LENGTH]} --> {self.author[:MAX_LENGTH]}'
