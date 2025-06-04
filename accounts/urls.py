from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,UserLoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/login/', UserLoginView.as_view(), name='user-login'),
    path('', include(router.urls)),  
]