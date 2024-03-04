from djoser.serializers import UserSerializer
from django.db import transaction
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient
)

MIN_INGREDIENT_AMOUNT = 1


class CustomUserSerializer(UserSerializer):
    """Селиализатор модели User"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get("request").user
        return (
            user.follower.filter(following_id=obj.id).exists()
            if user.is_anonymous or user == obj else False
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели Рецепт-Ингредиент."""

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор: ингредиенты в рецепте."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для запроса GET."""

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredient'
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для всех остальных запросов помимо GET."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientAmountSerializer(
        many=True,
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

#    def validate_ingredients(self, value):
#        """Валидация ингредиентов."""
#        if not value:
#            raise serializers.ValidationError(
#                'Нужно добавить хотя бы один ингредиент.'
#            )
#        for ingredient in value:
#            if not int(ingredient.get('amount')) >= MIN_INGREDIENT_AMOUNT:
#                raise serializers.ValidationError(
#                    'Количество ингредиентов не должно быть меньше 1.'
#                )
#        id_list = [ingredient.get('id') for ingredient in value]
#        if len(id_list) != len(set(id_list)):
#            raise serializers.ValidationError(
#                'Задвоение ингредиента.'
#            )
#        return value

#    def validate(self, data):
#        if not data['ingredients']:
#            raise serializers.ValidationError(
#                'Нужно добавить ингредиенты.'
#            )
#        return data

#    def validate_ingredients(self, ingredients):
#        ingredients_list = []
#        if not ingredients:
#            raise serializers.ValidationError(
#                'Нужно добавить ингредиенты.'
#            )
#        for ingredient in ingredients:
#            if ingredient['id'] in ingredients_list:
 #               raise serializers.ValidationError(
  #                  'Ингридиенты должны быть уникальны')
#            ingredients_list.append(ingredient['id'])
#            if int(ingredient.get('amount')) < 1:
#                raise serializers.ValidationError(
#                    'Количество ингредиента больше 0')
#            if int(ingredient.get('amount')) > 32000:
#                raise serializers.ValidationError(
#                    'Количество ингредиента больше 32000')
#        return ingredients

    def validate_tags(self, value):
        """Валидация тегов."""
        if not value:
            raise serializers.ValidationError(
                'Нужно добавить больше тегов.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Задвоение тега.'
            )
        return value

#    def validate(self, data):
#        """
#        Проверяет валидность данных при создании рецепта.
#        """
#        author = self.context['request'].user
#        name = data.get('name')
#        if self.instance is None and Recipe.objects.filter(
#            author=author,
#            name=name,
#        ).exists():
#            raise serializers.ValidationError(
#                {'error': 'Этот рецепт уже был добавлен.'}
#            )
#        return data

    def to_representation(self, instance):
        """Переопределение сериализатора для вывода данных."""
        return RecipeGetSerializer(
            instance, context=self.context
        ).data

    @transaction.atomic
    def create_and_update_objects(self, recipe, ingredients, tags):
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        RecipeIngredient.objects.bulk_create(ingredients_list)

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_and_update_objects(
            recipe=recipe,
            ingredients=ingredients,
            tags=tags
        )
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        """Редактирование рецепта."""
        recipe.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        self.create_and_update_objects(
            recipe=recipe,
            ingredients=ingredients,
            tags=tags
        )
        return recipe


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов в подписках и корзине."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        """Расчет количества рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Ограничение количества рецептов в подписках."""
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit := self.context['request'].GET.get(
                'recipes_limit'
        ):
            queryset = queryset[:int(recipes_limit)]
        return RecipesShortSerializer(
            queryset,
            many=True
        ).data
