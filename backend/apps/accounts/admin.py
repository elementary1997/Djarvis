"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = [
        'timezone', 'language', 'notifications_enabled',
        'receive_marketing_emails', 'total_points', 'streak_days'
    ]
    readonly_fields = ['total_points', 'streak_days', 'last_activity']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    inlines = [UserProfileInline]
    
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'role', 'is_active', 'is_email_verified', 'created_at'
    ]
    list_filter = [
        'role', 'is_active', 'is_email_verified',
        'is_staff', 'created_at'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'bio', 'avatar', 'github_username')
        }),
        (_('Permissions'), {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'is_email_verified', 'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name', 'role'
            ),
        }),
    )
