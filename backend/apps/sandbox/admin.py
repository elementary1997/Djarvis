"""
Admin interface for sandbox.
"""
from django.contrib import admin
from .models import SandboxSession


@admin.register(SandboxSession)
class SandboxSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'container_name', 'status', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'container_name', 'container_id']
    readonly_fields = ['container_id', 'container_name', 'created_at', 'last_activity']
    ordering = ['-created_at']
