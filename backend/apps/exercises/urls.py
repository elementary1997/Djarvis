"""
URL routing for exercises app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, SubmissionViewSet

app_name = 'exercises'

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]
