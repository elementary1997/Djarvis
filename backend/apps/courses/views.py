"""
Views for courses app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    Course, Module, Lesson,
    CourseEnrollment, LessonCompletion
)
from .serializers import (
    CourseSerializer, CourseListSerializer,
    ModuleSerializer, ModuleListSerializer,
    LessonSerializer, LessonListSerializer,
    CourseEnrollmentSerializer,
    LessonCompletionSerializer,
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Course model."""
    
    queryset = Course.objects.filter(is_published=True).prefetch_related('modules__lessons')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    @extend_schema(
        summary="List all courses",
        description="Get list of all published courses.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get course details",
        description="Get detailed information about a specific course.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Enroll in course",
        description="Enroll authenticated user in the course.",
        responses={201: CourseEnrollmentSerializer},
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll user in course."""
        course = self.get_object()
        
        # Check if already enrolled
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'is_active': True}
        )
        
        if not created:
            if enrollment.is_active:
                return Response(
                    {'detail': 'Already enrolled in this course.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Re-activate enrollment
                enrollment.is_active = True
                enrollment.save()
        
        serializer = CourseEnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Unenroll from course",
        description="Unenroll authenticated user from the course.",
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unenroll(self, request, slug=None):
        """Unenroll user from course."""
        course = self.get_object()
        
        enrollment = get_object_or_404(
            CourseEnrollment,
            user=request.user,
            course=course
        )
        
        enrollment.is_active = False
        enrollment.save()
        
        return Response(
            {'detail': 'Successfully unenrolled from course.'},
            status=status.HTTP_200_OK
        )


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Module model."""
    
    queryset = Module.objects.filter(is_published=True).prefetch_related('lessons')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ModuleListSerializer
        return ModuleSerializer
    
    def get_queryset(self):
        """Filter modules by course if course_slug is provided."""
        queryset = super().get_queryset()
        course_slug = self.request.query_params.get('course_slug')
        
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)
        
        return queryset
    
    @extend_schema(
        summary="List modules",
        description="Get list of all published modules, optionally filtered by course.",
        parameters=[
            OpenApiParameter(
                name='course_slug',
                description='Filter modules by course slug',
                required=False,
                type=str
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Lesson model."""
    
    queryset = Lesson.objects.filter(is_published=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer
    
    def get_queryset(self):
        """Filter lessons by module if module_slug is provided."""
        queryset = super().get_queryset()
        module_slug = self.request.query_params.get('module_slug')
        
        if module_slug:
            queryset = queryset.filter(module__slug=module_slug)
        
        return queryset
    
    @extend_schema(
        summary="List lessons",
        description="Get list of all published lessons, optionally filtered by module.",
        parameters=[
            OpenApiParameter(
                name='module_slug',
                description='Filter lessons by module slug',
                required=False,
                type=str
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Mark lesson as complete",
        description="Mark lesson as completed by authenticated user.",
        responses={201: LessonCompletionSerializer},
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, slug=None):
        """Mark lesson as completed."""
        lesson = self.get_object()
        time_spent = request.data.get('time_spent_minutes', 0)
        
        # Create or update completion
        completion, created = LessonCompletion.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'time_spent_minutes': time_spent}
        )
        
        # Update course progress
        self._update_course_progress(request.user, lesson)
        
        serializer = LessonCompletionSerializer(completion)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)
    
    def _update_course_progress(self, user, lesson):
        """Update user's progress in the course."""
        course = lesson.module.course
        enrollment = CourseEnrollment.objects.filter(
            user=user,
            course=course,
            is_active=True
        ).first()
        
        if not enrollment:
            return
        
        # Calculate progress
        total_lessons = course.total_lessons
        completed_lessons = LessonCompletion.objects.filter(
            user=user,
            lesson__module__course=course
        ).count()
        
        if total_lessons > 0:
            progress = int((completed_lessons / total_lessons) * 100)
            enrollment.progress_percentage = progress
            
            # Mark course as completed if all lessons done
            if progress >= 100 and not enrollment.completed_at:
                enrollment.completed_at = timezone.now()
            
            enrollment.save()


class UserEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user's course enrollments."""
    
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return enrollments for current user."""
        return CourseEnrollment.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('course').prefetch_related('course__modules__lessons')
    
    @extend_schema(
        summary="List user enrollments",
        description="Get list of courses the authenticated user is enrolled in.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
