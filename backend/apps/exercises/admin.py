"""
Admin interface for exercises.
"""
from django.contrib import admin
from .models import Exercise, ExerciseAttempt


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'difficulty', 'xp_reward', 'order', 'is_published']
    list_filter = ['difficulty', 'is_published', 'lesson__module']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['lesson', 'order']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('lesson', 'title', 'slug', 'description', 'instructions')
        }),
        ('Code', {
            'fields': ('starter_code', 'solution_code')
        }),
        ('Testing', {
            'fields': ('test_cases', 'hints')
        }),
        ('Settings', {
            'fields': ('difficulty', 'xp_reward', 'order', 'time_limit_seconds', 'max_attempts', 'is_published')
        }),
    )


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'is_passed', 'execution_time', 'attempt_number', 'created_at']
    list_filter = ['is_passed', 'exercise__difficulty', 'created_at']
    search_fields = ['user__email', 'exercise__title']
    readonly_fields = ['attempt_number', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
