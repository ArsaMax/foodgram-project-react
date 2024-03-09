from django.urls import path, include
from rest_framework import routers

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet
)

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(
    'recipes',
    RecipeViewSet,
    basename='recipe'
)
v1_router.register(
    'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(v1_router.urls)),
]
