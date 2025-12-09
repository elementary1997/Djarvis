"""
Admin interface для управления пользователями.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin с дополнительными полями."""
    
    list_display = [
        'email',
        'username',
        'total_points',
        'total_exercises_completed',
        'current_streak',
        'is_staff',
        'is_active',
        'created_at',
    ]
    list_filter = ['is_staff', 'is_active', 'theme', 'email_notifications', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'bio', 'avatar')}),
        (_('Statistics'), {
            'fields': (
                'total_exercises_completed',
                'total_points',
                'current_streak',
                'longest_streak',
                'last_activity_date',
            )
        }),
        (_('Settings'), {'fields': ('theme', 'email_notifications')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
