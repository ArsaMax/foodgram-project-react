from django.contrib import admin

from . import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'text', 'cooking_time', 'image', 'author', 'pub_date'
    )
#    list_editable = ('name', 'cooking_time', 'image', 'author')
    list_filter = ('name', 'author', 'tags')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
#    list_editable = ('name', 'color', 'slug')


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
#    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
#    list_editable = ('user', 'recipe')


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
#    list_editable = ('user', 'recipe')
