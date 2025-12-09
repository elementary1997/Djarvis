"""
URL routing for courses app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    ModuleViewSet,
    LessonViewSet,
    UserEnrollmentViewSet,
)

app_name = 'courses'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'my-enrollments', UserEnrollmentViewSet, basename='user-enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
