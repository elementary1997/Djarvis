"""
Admin configuration for exercises app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Exercise, Hint, Submission, HintUsage


class HintInline(admin.TabularInline):
    """Inline admin for hints."""
    model = Hint
    extra = 1
    fields = ['order', 'content', 'points_penalty']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin configuration for Exercise model."""
    
    list_display = [
        'title', 'lesson', 'difficulty', 'points',
        'max_attempts', 'is_published', 'created_at'
    ]
    list_filter = ['difficulty', 'is_published', 'lesson__module__course', 'created_at']
    search_fields = ['title', 'description', 'lesson__title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [HintInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'title', 'slug', 'description', 'difficulty')
        }),
        ('Code Templates', {
            'fields': ('initial_code', 'solution_code', 'inventory_template'),
            'classes': ('wide',)
        }),
        ('Configuration', {
            'fields': (
                'order', 'points', 'max_attempts',
                'time_limit_seconds', 'test_cases'
            )
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
    )


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    """Admin configuration for Hint model."""
    
    list_display = ['exercise', 'order', 'points_penalty', 'created_at']
    list_filter = ['exercise__lesson__module__course', 'created_at']
    search_fields = ['exercise__title', 'content']
    
    fieldsets = (
        (None, {
            'fields': ('exercise', 'order', 'content', 'points_penalty')
        }),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for Submission model."""
    
    list_display = [
        'user', 'exercise', 'status_badge', 'attempt_number',
        'points_earned', 'execution_time_ms', 'submitted_at'
    ]
    list_filter = ['status', 'exercise__difficulty', 'submitted_at']
    search_fields = ['user__email', 'user__username', 'exercise__title']
    readonly_fields = ['submitted_at', 'ip_address']
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('user', 'exercise', 'attempt_number', 'ip_address')
        }),
        ('Code', {
            'fields': ('code',),
            'classes': ('wide',)
        }),
        ('Results', {
            'fields': (
                'status', 'output', 'error_message', 'test_results',
                'execution_time_ms', 'points_earned'
            )
        }),
        ('Hints', {
            'fields': ('hints_used',)
        }),
        ('Metadata', {
            'fields': ('submitted_at',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': '#6c757d',
            'running': '#0dcaf0',
            'passed': '#28a745',
            'failed': '#dc3545',
            'error': '#fd7e14',
            'timeout': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:3px; font-weight:bold;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(HintUsage)
class HintUsageAdmin(admin.ModelAdmin):
    """Admin configuration for HintUsage model."""
    
    list_display = ['user', 'hint', 'revealed_at']
    list_filter = ['revealed_at', 'hint__exercise']
    search_fields = ['user__email', 'user__username', 'hint__exercise__title']
    readonly_fields = ['revealed_at']
