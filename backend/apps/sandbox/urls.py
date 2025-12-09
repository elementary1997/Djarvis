"""
URL patterns for sandbox app.
"""
from django.urls import path
from .views import CreateSandboxView, ExecuteCodeView, DestroySandboxView

app_name = 'sandbox'

urlpatterns = [
    path('create/', CreateSandboxView.as_view(), name='create'),
    path('execute/', ExecuteCodeView.as_view(), name='execute'),
    path('destroy/', DestroySandboxView.as_view(), name='destroy'),
]
