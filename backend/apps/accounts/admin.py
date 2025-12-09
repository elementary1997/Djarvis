"""
Admin interface for user accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Achievement, UserAchievement


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'level', 'total_xp', 'is_verified', 'is_staff', 'date_joined'
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_verified', 'level']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'avatar', 'bio')}),
        (_('Gamification'), {'fields': ('total_xp', 'level', 'preferred_language')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin interface for Achievement model."""
    
    list_display = [
        'name', 'icon', 'requirement_type', 'requirement_value',
        'xp_reward', 'is_active'
    ]
    list_filter = ['requirement_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['requirement_value']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin interface for UserAchievement model."""
    
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['achievement', 'unlocked_at']
    search_fields = ['user__email', 'user__username', 'achievement__name']
    ordering = ['-unlocked_at']
    raw_id_fields = ['user', 'achievement']
