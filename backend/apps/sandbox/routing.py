"""
WebSocket routing для real-time обновлений выполнения.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sandbox/(?P<execution_id>\w+)/$', consumers.SandboxConsumer.as_asgi()),
]
