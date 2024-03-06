from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

MAX_LENGTH = 10
MIN_VALUE = 1
MAX_VALUE = 32000


class RecipeQuerySet(models.QuerySet):
    """QuerySet для модели рецептов."""

    def with_favorited_and_in_cart_status(self, user):
        return self.annotate(
            is_favorited=models.Exists(
                Favorite.objects.filter(
                    recipe=models.OuterRef('pk'),
                    user=user
                )
            ),
            is_in_shopping_cart=models.Exists(
                Cart.objects.filter(
                    recipe=models.OuterRef('pk'),
                    user=user
                )
            )
        )


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Тег',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        'Цвет',
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Наименование ингредиента',
        unique=True,
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта (мэни ту мэни: ингредиенты и тэги)."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Теги',
    )
    name = models.CharField(
        'Рецепт',
        max_length=200,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(limit_value=MIN_VALUE,),
            MaxValueValidator(limit_value=MAX_VALUE,)

        ),
        verbose_name='Время приготовления, мин.',
    )
    text = models.TextField(
        'Описание',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    objects = models.Manager.from_queryset(
        RecipeQuerySet
    )()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель добавления в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_favorites'
        ),)


class RecipeIngredient(models.Model):
    """Промежуточная модель рецепт-ингредиент."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        )
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_ingredient'
        ),)


class Cart(models.Model):
    """Модель для корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Владелец корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_cart'
        ),)
