from django.urls import path,include
from rest_framework import routers
from .views import UserRegistrationViewset, UserLoginViewset, becomeInstructor

user_router = routers.DefaultRouter()
user_router.register(r'register', UserRegistrationViewset, basename='register')
user_router.register(r'login', UserLoginViewset, basename='login')


urlpatterns = [
    path('', include(user_router.urls)),
    path('becomeinstructor',becomeInstructor),
]