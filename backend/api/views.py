from django.db.models import Sum, Prefetch
from django.http import HttpResponse
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from users.models import Follow, User
from recipes.models import (
    Tag, Ingredient,
    Recipe, Cart,
    Favorite
)

from .filters import IngredientSearchFilter, RecipeSearchFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipesShortSerializer,
    SubscriptionsSerializer, RecipeGetSerializer,
    CustomUserSerializer
)
from .pagination import CustomPagination


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Вывод информации о текущем пользователе."""
        user = get_object_or_404(
            User,
            email=request.user.email
        )
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        methods=('get',),
        detail=False
    )
    def subscriptions(self, request):
        """Вывод списка подписок пользователя."""
        user = request.user
        following = User.objects.filter(
            following__user=user
        ).annotate(recipes_count=Count('recipes'))
        paginate = self.paginate_queryset(following)
        serializer = SubscriptionsSerializer(
            data=paginate,
            many=True,
            context={
                'request': request
            }
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Создание подписки."""
        user = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if request.user == user:
            return Response(
                'Нельзя подписаться на себя.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
                user=request.user,
                following=user
        ).first():
            return Response(
                data='Вы уже подписаны.',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            following=user
        )
        serializer = SubscriptionsSerializer(
            user,
            context={
                'request': request
            }
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Удаление подписки."""
        user = get_object_or_404(
            User,
            id=kwargs.get('id')
        )
        if following := Follow.objects.filter(
            following=user,
            user=request.user
        ).first():
            following.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data='Вы не подписаны на этого пользователя.',
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов с реализованным функционалом избранных рецептом и
    скачивания списка покупок.
    """

    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related(Prefetch('ingredients'))
        .all()
    )
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.with_favorited_and_in_cart_status(
                self.request.user
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def create_object(
            self, model, text, serializer
    ):
        """Добавление рецепта в избранное или корзину."""
        if not (recipe := Recipe.objects.filter(
                id=self.kwargs.get('pk')
        ).first()):
            return Response(
                'Рецепт не существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(
                recipe=recipe, user=self.request.user
        ).exists():
            return Response(
                f'Рецепт уже в {text}.',
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(
            recipe=recipe,
            user=self.request.user
        )
        serializer = serializer(
            recipe,
            context={
                'request': self.request
            }
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_object(
            self, model, text
    ):
        """Удаление рецепта из избранного и корзины."""
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('pk')
        )
        if obj := model.objects.filter(
                recipe=recipe, user=self.request.user
        ):
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            f'Данного рецепта нет в {text}.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('post',),
        detail=True
    )
    def favorite(self, request, **kwargs):
        """Добавление рецепта в избранное."""
        text = 'избранном'
        return self.create_object(
            model=Favorite,
            text=text,
            serializer=RecipesShortSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        """Удаление рецепта из избранного."""
        text = 'избранном'
        return self.delete_object(
            model=Favorite,
            text=text
        )

    @action(
        methods=('post',),
        detail=True
    )
    def shopping_cart(self, request, **kwargs):
        """Добавление рецепта в избранное."""
        text = 'корзине'
        return self.create_object(
            model=Cart,
            text=text,
            serializer=RecipesShortSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        text = 'корзине'
        return self.delete_object(
            model=Cart,
            text=text
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в PDF."""
        recipes = Recipe.objects.filter(
            cart_recipes__user=request.user
        )
        ingredients = Ingredient.objects.filter(
            recipe_ingredient__recipe__in=recipes
        )
        queryset_ingredients = ingredients.annotate(
            sum_amount_ingredients=(
                Sum('recipe_ingredient__amount')
            )
        )
        response = HttpResponse(content_type='application/pdf')
        pdfmetrics.registerFont(
            TTFont(
                'FreeSans',
                'static/fonts/FreeSans.ttf'
            )
        )
        pdf_canvas = canvas.Canvas(response)
        text_object = pdf_canvas.beginText(100, 730)
        text_object.setFont('FreeSans', 12)
        text_object.textLine('Список покупок:')
        for ingredient in queryset_ingredients:
            pdf_text = (f'{ingredient.name} '
                        f'({ingredient.measurement_unit}) — '
                        f'{ingredient.sum_amount_ingredients}')
            text_object.textLine(pdf_text)
        pdf_canvas.drawText(text_object)
        pdf_canvas.setTitle('Ваш список покупок')
        pdf_canvas.save()
        return response
