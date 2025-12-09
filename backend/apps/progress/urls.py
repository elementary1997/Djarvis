"""
URL routes для progress app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'progress'

# TODO: Add viewsets
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
