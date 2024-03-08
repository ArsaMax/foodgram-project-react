from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from .models import (
    Recipe, Tag, Ingredient, Favorite,
    RecipeIngredient, Cart
)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)
    min_num = 1
    extra = 0
    validate_min = True


@admin.register(Recipe)
class RecipAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author'
    )
    list_editable = ('name', 'cooking_time')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'cooking_time')
    min_num = 1
    inlines = [IngredientInline]
    validate_min = True

    def favorites(self, obj):
        if Favorite.objects.filter(recipe=obj).exists():
            return Favorite.objects.filter(recipe=obj).count()
        return 0

#    def save_form(self, form):
#        if form['ingredient'] < 1:
#            raise ValueError
#        return form.save(commit=False)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')
    list_editable = ('name', 'color')
    list_filter = ('name', 'color')
    search_fields = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
