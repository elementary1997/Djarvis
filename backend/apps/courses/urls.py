"""
URL routes для courses app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'courses'

# TODO: Add viewsets
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
