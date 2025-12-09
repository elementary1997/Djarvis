"""
URL patterns for progress app.
"""
from django.urls import path
from .views import (
    UserProgressOverviewView,
    ModuleProgressListView,
    LessonProgressListView,
    MarkLessonCompleteView,
    DailyStreakView,
    LeaderboardView
)

app_name = 'progress'

urlpatterns = [
    path('overview/', UserProgressOverviewView.as_view(), name='overview'),
    path('modules/', ModuleProgressListView.as_view(), name='module_progress'),
    path('lessons/', LessonProgressListView.as_view(), name='lesson_progress'),
    path('lessons/complete/', MarkLessonCompleteView.as_view(), name='mark_complete'),
    path('streak/', DailyStreakView.as_view(), name='streak'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
