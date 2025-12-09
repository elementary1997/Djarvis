"""
Admin interface for courses.
"""
from django.contrib import admin
from .models import Module, Lesson, LessonResource


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'slug', 'order', 'xp_reward', 'is_published']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['icon', 'title', 'difficulty', 'order', 'total_lessons', 'is_published', 'created_at']
    list_filter = ['difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']
    inlines = [LessonInline]


class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'xp_reward', 'estimated_minutes', 'is_published']
    list_filter = ['module', 'is_published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['module', 'order']
    inlines = [LessonResourceInline]


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'resource_type', 'order']
    list_filter = ['resource_type']
    search_fields = ['title', 'description']
