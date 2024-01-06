from distutils.util import strtobool

import django_filters as filters
from recipes.models import Recipe, Favorite, Cart, Ingredient, Tag

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    author = CharFilterInFilter(
        field_name='author',
        lookup_expr='in'
    )
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='recipetag__tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = Favorite.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = Cart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
