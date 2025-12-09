"""
URL routes для sandbox app.
"""
from django.urls import path
from .views import ExecuteCodeView, ExecutionStatusView, ExecutionHistoryView

app_name = 'sandbox'

urlpatterns = [
    path('execute/', ExecuteCodeView.as_view(), name='execute'),
    path('status/<str:task_id>/', ExecutionStatusView.as_view(), name='status'),
    path('history/', ExecutionHistoryView.as_view(), name='history'),
]
