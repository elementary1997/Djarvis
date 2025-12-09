"""
URL patterns for courses app.
"""
from django.urls import path
from .views import (
    ModuleListView,
    ModuleDetailView,
    LessonListView,
    LessonDetailView,
)

app_name = 'courses'

urlpatterns = [
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/<slug:slug>/', ModuleDetailView.as_view(), name='module_detail'),
    path('modules/<slug:module_slug>/lessons/', LessonListView.as_view(), name='lesson_list'),
    path('modules/<slug:module_slug>/lessons/<slug:slug>/', LessonDetailView.as_view(), name='lesson_detail'),
]
