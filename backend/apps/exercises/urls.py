"""
URL patterns for exercises app.
"""
from django.urls import path
from .views import (
    ExerciseListView,
    ExerciseDetailView,
    ExerciseAttemptListView,
    GetHintView
)

app_name = 'exercises'

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('<int:exercise_id>/attempts/', ExerciseAttemptListView.as_view(), name='attempt_list'),
    path('<int:exercise_id>/hint/', GetHintView.as_view(), name='get_hint'),
]
