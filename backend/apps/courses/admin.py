"""
Admin configuration for courses app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Module, Lesson,
    CourseEnrollment, LessonCompletion
)


class ModuleInline(admin.TabularInline):
    """Inline admin for modules."""
    model = Module
    extra = 0
    fields = ['title', 'slug', 'order', 'is_published']
    prepopulated_fields = {'slug': ('title',)}


class LessonInline(admin.TabularInline):
    """Inline admin for lessons."""
    model = Lesson
    extra = 0
    fields = ['title', 'slug', 'lesson_type', 'order', 'estimated_minutes', 'is_published']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    
    list_display = [
        'title', 'difficulty', 'total_modules_display',
        'estimated_hours', 'is_published', 'created_at'
    ]
    list_filter = ['difficulty', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Configuration', {
            'fields': ('difficulty', 'estimated_hours', 'thumbnail', 'order')
        }),
        ('Publishing', {
            'fields': ('is_published', 'created_by')
        }),
    )
    
    def total_modules_display(self, obj):
        return obj.total_modules
    total_modules_display.short_description = 'Modules'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin configuration for Module model."""
    
    list_display = [
        'title', 'course', 'order',
        'total_lessons_display', 'is_published'
    ]
    list_filter = ['course', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        ('Configuration', {
            'fields': ('order', 'is_published')
        }),
    )
    
    def total_lessons_display(self, obj):
        return obj.total_lessons
    total_lessons_display.short_description = 'Lessons'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin configuration for Lesson model."""
    
    list_display = [
        'title', 'module', 'lesson_type',
        'order', 'estimated_minutes', 'is_published'
    ]
    list_filter = ['lesson_type', 'is_published', 'module__course', 'created_at']
    search_fields = ['title', 'content', 'module__title']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'slug', 'lesson_type')
        }),
        ('Content', {
            'fields': ('content', 'video_url'),
            'classes': ('wide',)
        }),
        ('Configuration', {
            'fields': ('order', 'estimated_minutes', 'is_published')
        }),
    )


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for CourseEnrollment model."""
    
    list_display = [
        'user', 'course', 'progress_bar',
        'is_active', 'enrolled_at', 'completed_at'
    ]
    list_filter = ['is_active', 'course', 'enrolled_at']
    search_fields = ['user__email', 'user__username', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at']
    
    def progress_bar(self, obj):
        """Display progress as a colored bar."""
        percentage = obj.progress_percentage
        color = '#28a745' if percentage >= 75 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; border:1px solid #ccc;">'
            '<div style="width:{}px; background-color:{}; height:20px; text-align:center; color:white; font-weight:bold;">{}%</div>'
            '</div>',
            percentage, color, percentage
        )
    progress_bar.short_description = 'Progress'


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    """Admin configuration for LessonCompletion model."""
    
    list_display = [
        'user', 'lesson', 'completed_at', 'time_spent_minutes'
    ]
    list_filter = ['completed_at', 'lesson__module__course']
    search_fields = ['user__email', 'user__username', 'lesson__title']
    readonly_fields = ['completed_at']
