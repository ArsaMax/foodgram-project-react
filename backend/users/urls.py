from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CustomUserViewSet

app_name = 'users'

v1_router = DefaultRouter()
v1_router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    url(r'^', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
