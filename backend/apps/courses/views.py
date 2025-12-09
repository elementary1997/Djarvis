"""
Views for courses and lessons.
"""
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Module, Lesson
from .serializers import (
    ModuleListSerializer,
    ModuleDetailSerializer,
    LessonListSerializer,
    LessonDetailSerializer,
)


class ModuleListView(generics.ListAPIView):
    """
    API endpoint for listing all modules.
    
    GET /api/courses/modules/
    """
    queryset = Module.objects.filter(is_published=True)
    serializer_class = ModuleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['order']


class ModuleDetailView(generics.RetrieveAPIView):
    """
    API endpoint for module detail.
    
    GET /api/courses/modules/{slug}/
    """
    queryset = Module.objects.filter(is_published=True)
    serializer_class = ModuleDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'


class LessonListView(generics.ListAPIView):
    """
    API endpoint for listing lessons in a module.
    
    GET /api/courses/modules/{module_slug}/lessons/
    """
    serializer_class = LessonListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_slug = self.kwargs.get('module_slug')
        return Lesson.objects.filter(
            module__slug=module_slug,
            is_published=True
        ).order_by('order')


class LessonDetailView(generics.RetrieveAPIView):
    """
    API endpoint for lesson detail.
    
    GET /api/courses/modules/{module_slug}/lessons/{slug}/
    """
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        module_slug = self.kwargs.get('module_slug')
        return Lesson.objects.filter(
            module__slug=module_slug,
            is_published=True
        )
