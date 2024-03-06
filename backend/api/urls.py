from django.urls import path, include
from rest_framework import routers

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipe'
)

urlpatterns = [
    path('', include(v1_router.urls)),
]
