from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.views import UserViewSet

from .filters import RecipeFilter, IngredientFilter
from .pagination import CustomPagination
from .serializers import (
    CreateRecipeSerializer, RecipeSerializer, CartSerializer,
    SubscriptionSerializer, ShowSubscriptionsSerializer, FavoriteSerializer,
    TagSerializer, IngredientSerializer, CustomUserCreateSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, Tag, Cart
)
from users.models import Subscription, User
from .permissions import IsAuthorOrAdminOrReadOnly


class UsersViewSet(UserViewSet):
    pagination_class = CustomPagination

    def retrieve(self, *args, **kwargs):
        queryset = User.objects.all()
        id_ = kwargs.get('id')
        if self.action == 'me':
            id_ = self.request.user.id
        user = get_object_or_404(queryset, id=id_)
        serializer = CustomUserCreateSerializer(user)
        return Response(serializer.data)


class SubscribeView(APIView):
    """ Операция подписки/отписки. """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, id_):
        data = {
            'user': request.user.id,
            'author': id_
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id_):
        author = get_object_or_404(User, id=id_)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if subscription.exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """ Отображение подписок. """

    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteView(APIView):
    """ Добавление/удаление рецепта из избранного. """

    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def post(self, request, id_):
        data = {
            'user': request.user.id,
            'recipe': id_
        }
        if not Favorite.objects.filter(
           user=request.user, recipe__id=id_).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id_):
        recipe = get_object_or_404(Recipe, id=id_)
        favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Отображение тегов. """

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Отображение ингредиентов. """

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ReceiptViewSet(viewsets.ModelViewSet):
    """ Операции с рецептами: добавление/изменение/удаление/просмотр. """

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ShoppingCartView(APIView):
    """ Добавление рецепта в корзину или его удаление. """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, id_):
        data = {
            'user': request.user.id,
            'recipe': id_
        }
        recipe = get_object_or_404(Recipe, id=id_)
        if not Cart.objects.filter(
           user=request.user, recipe=recipe).exists():
            serializer = CartSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id_):
        recipe = get_object_or_404(Recipe, id=id_)
        shopping_cart = Cart.objects.filter(
           user=request.user, recipe=recipe
        )
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
