from django.urls import path,include
from rest_framework import routers
from .views import CourseViewSet,ModuleViewSet,ContentViewset

course_router = routers.DefaultRouter()
course_router.register(r'courses', CourseViewSet, basename='courses')
course_router.register(r'modules', ModuleViewSet, basename='modules')
course_router.register(r'content', ContentViewset, basename='content')

urlpatterns = [
    path('', include(course_router.urls)),
]