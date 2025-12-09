"""
Admin interface for progress tracking.
"""
from django.contrib import admin
from .models import ModuleProgress, LessonProgress, DailyStreak


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'completion_percentage', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'module']
    search_fields = ['user__email', 'user__username', 'module__title']
    readonly_fields = ['completion_percentage', 'started_at', 'completed_at']
    ordering = ['-started_at']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'time_spent_minutes', 'last_accessed']
    list_filter = ['is_completed', 'lesson__module']
    search_fields = ['user__email', 'user__username', 'lesson__title']
    readonly_fields = ['last_accessed', 'completed_at']
    ordering = ['-last_accessed']
    
    def time_spent_minutes(self, obj):
        return f"{obj.time_spent // 60} min"
    time_spent_minutes.short_description = 'Time Spent'


@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['last_activity_date']
    ordering = ['-current_streak']
