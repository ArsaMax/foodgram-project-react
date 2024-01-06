from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import User

MAX_AMOUNT = 1000
MIN_VALUE = 1
MAX_COOKING_TIME = 360
MAX_LENGTH = 10


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:MAX_LENGTH]


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Тег',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        'Цвет',
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_LENGTH]


class Recipe(models.Model):
    """Модель рецепта (мэни ту мэни: ингредиенты и тэги)."""

    name = models.CharField(
        'Рецепт',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Описание',
        null=True,
        default=None,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='media/',
        null=True,
        default=None,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Игредиенты',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            MIN_VALUE), MaxValueValidator(MAX_COOKING_TIME)],
        verbose_name='Время приготовления, мин.',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:MAX_LENGTH]


class RecipeIngredient(models.Model):
    """Промежуточная модель рецепт-ингредиент."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Игредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            MIN_VALUE), MaxValueValidator(MAX_AMOUNT)],
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'В рецепте {self.recipe[:MAX_LENGTH]} '
                f'ингредиенты: {self.ingredient[:MAX_LENGTH]}.')


class RecipeTag(models.Model):
    """Промежуточная модель рецепт-тег."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return (f'Тег {self.tag[:MAX_LENGTH]} '
                f'у рецепта {self.recipe[:MAX_LENGTH]}')


class Favorite(models.Model):
    """Модель добавления в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Избранный'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user[:MAX_LENGTH]} - {self.recipe[:MAX_LENGTH]}'


class Cart(models.Model):
    """Модель для корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Владелец корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.user[:MAX_LENGTH]} - {self.recipe[:MAX_LENGTH]}'


class Follow(models.Model):
    """Система подписок"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписки'
        verbose_name_plural = 'Подписки'
