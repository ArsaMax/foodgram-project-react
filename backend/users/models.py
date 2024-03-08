from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


ALLOWED_SYMBOLS = RegexValidator(
    r'^[\w.@+-]+\Z', 'Запрещенные символы в логине.'
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Логин',
        unique=True,
        max_length=150,
        validators=(ALLOWED_SYMBOLS,),
    )
    email = models.EmailField(
        'E-mail',
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписки пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчики',
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    def clean(self):
        if self.user == self.following:
            raise ValidationError('Подписка на себя запрещена.')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
