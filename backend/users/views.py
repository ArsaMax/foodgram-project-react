from api.pagination import CustomPagination
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.serializers import FollowSerializer, SubscriptionSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    lookup_field = 'id'
    search_fields = ('username',)

    @action(
        methods=('get',),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_self_page(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('get',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        is_subscribed = Subscription.objects.filter(
            user=self.request.user,
            author=OuterRef('id')
        )
        queryset = self.paginate_queryset(
            User.objects.filter(
                following__user=request.user).annotate(
                    is_subscribed=Exists(is_subscribed)).annotate(
                        recipes_count=Count('recipes')
            )
        )
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        following = get_object_or_404(Subscription, user=user, author=author)
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
